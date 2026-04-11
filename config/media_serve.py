"""
Serve user-uploaded files only to signed-in users.

Public ``static(MEDIA_URL, ...)`` would expose ``/media/materials/...`` without auth,
bypassing ``material_open`` / ``material_download``.
"""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.static import serve


@login_required
def protected_media(request, path):
    return serve(request, path, document_root=settings.MEDIA_ROOT)
