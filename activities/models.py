# teaching activities models

from django.db import models


class Category(models.Model):
    # groups activities together (e.g. "Icebreakers", "Projects")

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    # e.g. "group", "homework", "outside classroom"

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Activity(models.Model):
    # one activity per folder

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, through="ActivityTag", related_name="activities")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "activities"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"], name="idx_activity_title"),
            models.Index(fields=["category"], name="idx_activity_category_id"),
        ]

    def __str__(self):
        return self.title


class ActivityTag(models.Model):
    # links activities to tags

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="activity_tags",
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="activity_tags",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["activity", "tag"]]
        indexes = [
            models.Index(fields=["activity"], name="idx_activity_tag_activity_id"),
            models.Index(fields=["tag"], name="idx_activity_tag_tag_id"),
        ]

    def __str__(self):
        return f"{self.activity.title} — {self.tag.name}"


class Material(models.Model):
    # worksheets, instructions, examples, videos lives in media folder

    class MaterialType(models.TextChoices):
        WORKSHEET = "worksheet", "Worksheet"
        INSTRUCTIONS = "instructions", "Instructions"
        EXAMPLE = "example", "Example"
        VIDEO = "video", "Video"

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="materials",
    )
    title = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    material_type = models.CharField(
        max_length=20,
        choices=MaterialType.choices,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["activity"], name="idx_material_activity_id"),
            models.Index(fields=["material_type"], name="idx_material_type"),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_material_type_display()})"
