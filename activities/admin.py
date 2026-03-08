from django.contrib import admin
from .models import Category, Tag, Activity, ActivityTag, Material


class ActivityTagInline(admin.TabularInline):
    model = ActivityTag
    extra = 1


class MaterialInline(admin.TabularInline):
    model = Material
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["title", "description"]
    inlines = [ActivityTagInline, MaterialInline]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["title", "activity", "material_type", "uploaded_at"]
    list_filter = ["material_type"]
    search_fields = ["title"]
