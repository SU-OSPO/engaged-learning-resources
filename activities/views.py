from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from .models import Activity, Category


@require_GET
def activity_list(request):
    """
    List activities with optional search and filters.
    Query params: q (search title), tag (filter by tag name), category (filter by category id)
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
            pass

    activities = [
        {
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "category": a.category.name if a.category else None,
            "category_id": a.category_id,
            "tags": [t.name for t in a.tags.all()],
            "created_at": a.created_at.isoformat(),
        }
        for a in qs
    ]

    return JsonResponse({"activities": activities, "count": len(activities)})


@require_GET
def activity_detail(request, pk):
    """Retrieve a single activity by id."""
    activity = get_object_or_404(
        Activity.objects.select_related("category").prefetch_related("tags", "materials"),
        pk=pk,
    )

    materials = [
        {
            "id": m.id,
            "title": m.title,
            "material_type": m.get_material_type_display(),
            "file_url": m.file.url if m.file else None,
            "uploaded_at": m.uploaded_at.isoformat(),
        }
        for m in activity.materials.all()
    ]

    return JsonResponse(
        {
            "id": activity.id,
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
