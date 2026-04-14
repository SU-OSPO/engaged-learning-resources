# teaching activities models

from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    # groups activities together (e.g. "Icebreakers", "Projects")

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"], name="idx_category_name"),
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    # e.g. "group", "homework", "outside classroom"

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    @property
    def display_name(self) -> str:
        """How the tag appears on the site (title-style); storage stays lowercase-friendly."""
        if not self.name:
            return ""
        out: list[str] = []
        for word in self.name.strip().split():
            out.append(
                "-".join(
                    (p[0].upper() + p[1:].lower()) if len(p) > 1 else p.upper()
                    for p in word.split("-")
                )
            )
        return " ".join(out)

    def __str__(self):
        return self.name


class Activity(models.Model):
    # one activity per folder

    slug = models.SlugField(max_length=255, unique=True, blank=True)
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
            models.Index(fields=["created_at"], name="idx_activity_created_at"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "activity"
            self.slug = base
            n = 1
            while Activity.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{n}"
                n += 1
        super().save(*args, **kwargs)

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
        return f"{self.activity.title} - {self.tag.name}"


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
    file = models.FileField(
        upload_to="materials/%Y/%m/",
        blank=True,
        null=True,
        help_text="Main file for download (e.g. Word). PDFs can use this field alone for preview + download.",
    )
    preview_pdf = models.FileField(
        upload_to="materials/previews/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Preview (PDF)",
        help_text="Optional PDF shown inline on the activity page. Use when File is Word/Office so faculty see a preview here and download the editable file.",
    )
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
