from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from config.error_handlers import json_error_response
from .models import Activity, Category, Tag


SORT_FIELDS = {"title", "-title", "created_at", "-created_at"}


def _get_filtered_queryset(request):
    """Build filtered activity queryset from request params."""
    qs = Activity.objects.select_related("category").prefetch_related("tags", "materials")

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(title__icontains=q)

    tag_name = request.GET.get("tag", "").strip()
    if tag_name:
        qs = qs.filter(tags__name__iexact=tag_name)

    category_id = request.GET.get("category", "").strip()
    if category_id:
        try:
            qs = qs.filter(category_id=int(category_id))
        except ValueError:
            return None, "Invalid category id."

    sort = request.GET.get("sort", "-created_at").strip()
    if sort in SORT_FIELDS:
        qs = qs.order_by(sort)
    else:
        qs = qs.order_by("-created_at")

    return qs, None


@require_GET
def activity_list(request):
    """
    List activities with optional search, filters, pagination, and sorting.
    Returns HTML for browsers, JSON for API requests.
    """
    qs, err = _get_filtered_queryset(request)
    if err:
        return json_error_response(400, detail=err)

    # Pagination
    try:
        per_page = max(1, min(100, int(request.GET.get("limit", 20))))
    except ValueError:
        per_page = 20
    paginator = Paginator(qs, per_page)
    try:
        page_num = max(1, int(request.GET.get("page", 1)))
    except ValueError:
        page_num = 1
    page_obj = paginator.get_page(page_num)

    # HTML response
    if "text/html" in request.META.get("HTTP_ACCEPT", ""):
        tags = list(Tag.objects.order_by("name").values("id", "name"))
        categories = list(Category.objects.order_by("name").values("id", "name", "description"))
        pagination_params = {k: v for k, v in request.GET.items() if k != "page"}
        pagination_base = urlencode(pagination_params) if pagination_params else ""
        return render(
            request,
            "activities/activity_list.html",
            {
                "activities": page_obj.object_list,
                "page_obj": page_obj,
                "total": paginator.count,
                "tags": tags,
                "categories": categories,
                "pagination_base": pagination_base,
            },
        )

    # JSON response
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
        for a in page_obj.object_list
    ]
    return JsonResponse(
        {
            "activities": activities,
            "count": len(activities),
            "total": paginator.count,
            "page": page_obj.number,
            "limit": per_page,
        }
    )


@require_GET
def activity_detail(request, slug):
    """Retrieve a single activity by slug. Returns HTML or JSON."""
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

    # HTML response
    if "text/html" in request.META.get("HTTP_ACCEPT", ""):
        materials_for_template = [{"title": m["title"], "material_type": m["material_type"], "file_url": m["file_url"]} for m in materials]
        return render(
            request,
            "activities/activity_detail.html",
            {"activity": activity, "materials": materials_for_template},
        )

    # JSON response
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
