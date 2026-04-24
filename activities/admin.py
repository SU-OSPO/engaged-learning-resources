from django import forms
from django.contrib import admin

admin.site.site_header = "TeachOrange administration"
admin.site.site_title = "TeachOrange admin"
from django.core.exceptions import ValidationError
from .models import Category, Tag, Activity, ActivityTag, Material


class TagAdminForm(forms.ModelForm):
    """Prevent duplicate tags (case-insensitive)."""

    class Meta:
        model = Tag
        fields = "__all__"

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise ValidationError("Tag name is required.")
        qs = Tag.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("A tag with this name already exists.")
        return name


class ActivityAdminForm(forms.ModelForm):
    """Require title for activity."""

    class Meta:
        model = Activity
        fields = "__all__"

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise ValidationError("Activity title is required.")
        return title


class ActivityTagInline(admin.TabularInline):
    model = ActivityTag
    extra = 1


class MaterialInline(admin.TabularInline):
    model = Material
    extra = 1
    fields = ("title", "material_type", "file", "preview_pdf")
    # activity is auto-set when adding via Activity; required when adding standalone


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    form = TagAdminForm
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    form = ActivityAdminForm
    list_display = ["title", "slug", "category", "created_at"]
    # Category only: date-based list_filter on created_at has caused 500s on some
    # PostgreSQL + admin setups; use search or ordering for time-based triage.
    list_filter = ["category"]
    search_fields = ["title", "description"]
    inlines = [ActivityTagInline, MaterialInline]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["title", "activity", "material_type", "has_preview_pdf", "uploaded_at"]
    list_filter = ["material_type"]
    search_fields = ["title"]

    @admin.display(boolean=True, ordering="preview_pdf", description="Preview PDF")
    def has_preview_pdf(self, obj):
        return bool(obj.preview_pdf)
