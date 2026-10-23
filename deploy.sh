#!/usr/bin/env bash
#
# Deploy TeachOrange on the production VPS (nginx + gunicorn, CloudPanel site).
#
# Run from the application directory, as the CloudPanel site user:
#     ./deploy.sh
#
# Normally invoked by .github/workflows/deploy.yml on every push to main, but it
# is safe to run by hand for a manual release or a rollback.
#
# This is a CloudPanel "Python" site: nginx reverse-proxies to gunicorn on APP_PORT.
# There is no systemd unit and no supervisor program - gunicorn runs as a bare
# process owned by the site user (PPID 1). Reloading therefore means sending
# SIGHUP to the master, which gracefully restarts workers with the new code.
# If the master is gone, this script starts one, since nothing else will.
#
#   Site user:  teachorange
#   App dir:    /home/teachorange/htdocs/www.teachorange.com
#   Venv:       $APP_DIR/venv
#   App port:   8090
#
# Configuration (override in the environment or in .env beside this script):
#   APP_DIR      application directory              (default: this script's directory)
#   VENV_DIR     virtualenv to install into         (default: $APP_DIR/venv)
#   APP_PORT     port gunicorn listens on           (default: 8090)
#   GUNICORN_WORKERS  worker count when starting    (default: 3)
#   HEALTH_URL   URL that must return 200 after     (default: https://www.teachorange.com/)
#   BACKUP_DIR   where pg_dump files are written    (default: $APP_DIR/../db-backups)
#   SKIP_BACKUP  set to 1 to skip the pg_dump       (not recommended)

set -euo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
VENV_DIR="${VENV_DIR:-$APP_DIR/venv}"
GUNICORN_WORKERS="${GUNICORN_WORKERS:-3}"
APP_PORT="${APP_PORT:-8090}"
HEALTH_URL="${HEALTH_URL:-https://www.teachorange.com/}"
BACKUP_DIR="${BACKUP_DIR:-$APP_DIR/../db-backups}"
BRANCH="${DEPLOY_BRANCH:-main}"

cd "$APP_DIR"

log() { printf '\n==> %s\n' "$*"; }
PY="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

# --- 1. Remember where we are, so a failed deploy can be undone -------------
PREVIOUS_SHA="$(git rev-parse HEAD)"
log "Current revision: $PREVIOUS_SHA"

rollback() {
    log "DEPLOY FAILED — rolling back to $PREVIOUS_SHA"
    git reset --hard "$PREVIOUS_SHA"
    "$PIP" install --quiet -r requirements.txt || true
    "$PY" manage.py collectstatic --noinput || true
    restart_app || true
    echo
    echo "Rolled back to $PREVIOUS_SHA."
    echo "NOTE: database migrations are NOT rolled back. If this deploy applied a"
    echo "migration, restore from the dump in $BACKUP_DIR before serving traffic."
    exit 1
}

# The gunicorn master, i.e. the one whose parent is not itself a gunicorn.
gunicorn_master_pid() {
    local pids p ppid
    pids="$(pgrep -u "$(id -u)" -f 'gunicorn config.wsgi' 2>/dev/null || true)"
    [ -z "$pids" ] && return 1
    for p in $pids; do
        ppid="$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')"
        case " $pids " in
            *" $ppid "*) ;;           # parent is another gunicorn -> this is a worker
            *) echo "$p"; return 0 ;; # parent is not -> this is the master
        esac
    done
    return 1
}

start_gunicorn() {
    log "No gunicorn master found - starting one"
    mkdir -p "$HOME/logs"
    nohup "$VENV_DIR/bin/gunicorn" config.wsgi:application \
        --bind "127.0.0.1:$APP_PORT" \
        --workers "$GUNICORN_WORKERS" \
        --timeout 120 \
        --access-logfile "$HOME/logs/gunicorn-access.log" \
        --error-logfile "$HOME/logs/gunicorn-error.log" \
        >/dev/null 2>&1 &
    sleep 3
}

restart_app() {
    local master
    if master="$(gunicorn_master_pid)"; then
        # SIGHUP: graceful reload. Workers are replaced one at a time and pick up
        # the new code, so there is no dropped request. (Safe because gunicorn is
        # not running with --preload.)
        log "Reloading gunicorn master $master (SIGHUP)"
        kill -HUP "$master"
        sleep 3
    else
        start_gunicorn
    fi
}

# Confirm gunicorn is actually back up locally before trusting the public URL,
# so a failure is attributed to the app rather than to DNS/TLS/nginx.
wait_for_app_port() {
    for _ in $(seq 1 15); do
        if (exec 3<>"/dev/tcp/127.0.0.1/$APP_PORT") 2>/dev/null; then
            exec 3>&- 2>/dev/null || true
            return 0
        fi
        sleep 2
    done
    echo "WARNING: nothing listening on 127.0.0.1:$APP_PORT after restart" >&2
    return 1
}

# --- 2. Fetch the new code --------------------------------------------------
log "Fetching origin/$BRANCH"
git fetch --all --prune
git reset --hard "origin/$BRANCH"
TARGET_SHA="$(git rev-parse HEAD)"
log "Deploying $TARGET_SHA"

if [ "$TARGET_SHA" = "$PREVIOUS_SHA" ]; then
    log "Already at $TARGET_SHA — nothing to deploy, but continuing to refresh assets"
fi

# Everything past this point can fail, so arm the rollback.
trap rollback ERR

# --- 3. Dependencies --------------------------------------------------------
log "Installing dependencies"
"$PIP" install --quiet --upgrade pip
"$PIP" install --quiet -r requirements.txt

# --- 4. Back up the database BEFORE touching the schema ---------------------
# Migration 0004 is not safely reversible, so a dump is the only real undo.
if [ "${SKIP_BACKUP:-0}" != "1" ]; then
    if "$PY" -c "import django" 2>/dev/null && command -v pg_dump >/dev/null 2>&1; then
        mkdir -p "$BACKUP_DIR"
        STAMP="$(date +%Y%m%d-%H%M%S)"
        DUMP="$BACKUP_DIR/teachorange-$STAMP.sql"
        log "Backing up database to $DUMP"
        # Read connection settings from Django so this honours DATABASE_URL or POSTGRES_*.
        eval "$("$PY" - <<'PYEOF'
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.conf import settings
d = settings.DATABASES["default"]
print(f'export PGHOST={d.get("HOST") or "localhost"}')
print(f'export PGPORT={d.get("PORT") or 5432}')
print(f'export PGUSER={d.get("USER") or ""}')
print(f'export PGPASSWORD={d.get("PASSWORD") or ""}')
print(f'export PGDATABASE={d.get("NAME") or ""}')
PYEOF
)"
        pg_dump --no-owner --no-acl > "$DUMP"
        gzip -f "$DUMP"
        log "Backup written: $DUMP.gz"
        # Keep the 10 most recent dumps.
        ls -1t "$BACKUP_DIR"/teachorange-*.sql.gz 2>/dev/null | tail -n +11 | xargs -r rm --
    else
        log "WARNING: pg_dump unavailable — skipping backup"
    fi
fi

# --- 5. Migrate, collect static --------------------------------------------
log "Applying migrations"
"$PY" manage.py migrate --noinput

log "Collecting static files"
"$PY" manage.py collectstatic --noinput

# --- 6. Restart and health-check -------------------------------------------
restart_app
wait_for_app_port || true

log "Waiting for $HEALTH_URL to return 200"
for i in $(seq 1 10); do
    code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$HEALTH_URL" || true)"
    if [ "$code" = "200" ]; then
        trap - ERR
        log "Healthy (HTTP $code). Deployed $TARGET_SHA"
        exit 0
    fi
    echo "  attempt $i: HTTP $code"
    sleep 5
done

log "Health check never returned 200"
rollback
