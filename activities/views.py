from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from config.error_handlers import json_error_response
from .models import Activity, Category, Tag


SORT_FIELDS = {"title", "-title", "created_at", "-created_at"}


@require_GET
def activity_list(request):
    """
    List activities with optional search, filters, pagination, and sorting.
    Query params: q, tag, category, page, limit, sort
    """
    qs = Activity.objects.select_related("category").prefetch_related("tags", "materials")

    # Search by title
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(title__icontains=q)

    # Filter by tag
    tag_name = request.GET.get("tag", "").strip()
    if tag_name:
        qs = qs.filter(tags__name__iexact=tag_name)

    # Filter by category
    category_id = request.GET.get("category", "").strip()
    if category_id:
        try:
            qs = qs.filter(category_id=int(category_id))
        except ValueError:
            return json_error_response(400, detail="Invalid category id.")

    # Sorting
    sort = request.GET.get("sort", "-created_at").strip()
    if sort in SORT_FIELDS:
        qs = qs.order_by(sort)
    else:
        qs = qs.order_by("-created_at")

    # Pagination
    try:
        limit = max(1, min(100, int(request.GET.get("limit", 20))))
    except ValueError:
        limit = 20
    try:
        page = max(1, int(request.GET.get("page", 1)))
    except ValueError:
        page = 1
    offset = (page - 1) * limit

    total = qs.count()
    qs = qs[offset : offset + limit]

    activities = [
        {
            "id": a.id,
            "slug": a.slug,
            "title": a.title,
            "description": a.description,
            "category": a.category.name if a.category else None,
            "category_id": a.category_id,
            "tags": [t.name for t in a.tags.all()],
            "created_at": a.created_at.isoformat(),
        }
        for a in qs
    ]

    return JsonResponse(
        {
            "activities": activities,
            "count": len(activities),
            "total": total,
            "page": page,
            "limit": limit,
        }
    )


@require_GET
def activity_detail(request, slug):
    """Retrieve a single activity by slug."""
    activity = get_object_or_404(
        Activity.objects.select_related("category").prefetch_related("tags", "materials"),
        slug=slug,
    )

    materials = [
        {
            "id": m.id,
            "title": m.title,
            "material_type": m.get_material_type_display(),
            "file_url": request.build_absolute_uri(m.file.url) if m.file else None,
            "uploaded_at": m.uploaded_at.isoformat(),
        }
        for m in activity.materials.all()
    ]

    return JsonResponse(
        {
            "id": activity.id,
            "slug": activity.slug,
            "title": activity.title,
            "description": activity.description,
            "category": activity.category.name if activity.category else None,
            "category_id": activity.category_id,
            "tags": [t.name for t in activity.tags.all()],
            "materials": materials,
            "created_at": activity.created_at.isoformat(),
            "updated_at": activity.updated_at.isoformat(),
        }
    )


@require_GET
def tag_list(request):
    """List all tags for filter dropdowns."""
    tags = Tag.objects.order_by("name").values("id", "name")
    return JsonResponse({"tags": list(tags)})


@require_GET
def category_list(request):
    """List all categories for filter dropdowns."""
    categories = Category.objects.order_by("name").values("id", "name", "description")
    return JsonResponse({"categories": list(categories)})
