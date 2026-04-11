import json
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase, Client
from django.urls import reverse
from .models import Category, Tag, Activity, ActivityTag, Material


class ModelTests(TestCase):
    """Test models and relationships."""

    def test_create_category(self):
        cat = Category.objects.create(name="Icebreakers", description="Get started")
        self.assertEqual(cat.name, "Icebreakers")
        self.assertEqual(str(cat), "Icebreakers")

    def test_create_tag(self):
        tag = Tag.objects.create(name="group")
        self.assertEqual(tag.name, "group")
        self.assertEqual(str(tag), "group")

    def test_tag_unique_name(self):
        Tag.objects.create(name="homework")
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="homework")

    def test_create_activity_with_category_and_tags(self):
        cat = Category.objects.create(name="Projects")
        activity = Activity.objects.create(title="Scavenger Hunt", category=cat)
        tag1 = Tag.objects.create(name="group")
        tag2 = Tag.objects.create(name="outside")
        ActivityTag.objects.create(activity=activity, tag=tag1)
        ActivityTag.objects.create(activity=activity, tag=tag2)
        self.assertEqual(activity.title, "Scavenger Hunt")
        self.assertEqual(activity.category, cat)
        self.assertEqual(activity.tags.count(), 2)

    def test_material_linked_to_activity(self):
        activity = Activity.objects.create(title="Test Activity")
        material = Material.objects.create(
            activity=activity,
            title="Worksheet 1",
            material_type=Material.MaterialType.WORKSHEET,
        )
        self.assertEqual(material.activity, activity)
        self.assertIn("Worksheet", str(material))


class ActivityListTests(TestCase):
    """Test GET /activities/ endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="faculty@test.edu",
            email="faculty@test.edu",
            password="testpass123",
        )
        self.client.login(username="faculty@test.edu", password="testpass123")
        self.cat = Category.objects.create(name="Icebreakers")
        self.tag = Tag.objects.create(name="group")
        self.activity1 = Activity.objects.create(
            title="Scavenger Hunt",
            description="Find items outside",
            category=self.cat,
        )
        self.activity2 = Activity.objects.create(
            title="Team Building",
            description="Build trust",
            category=self.cat,
        )
        ActivityTag.objects.create(activity=self.activity1, tag=self.tag)

    def test_list_returns_all_activities(self):
        resp = self.client.get("/activities/")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["total"], 2)
        self.assertEqual(len(data["activities"]), 2)
        self.assertIn("slug", data["activities"][0])

    def test_search_by_title(self):
        resp = self.client.get("/activities/", {"q": "Scavenger"})
        data = json.loads(resp.content)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["activities"][0]["title"], "Scavenger Hunt")

    def test_filter_by_tag(self):
        resp = self.client.get("/activities/", {"tag": "group"})
        data = json.loads(resp.content)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["activities"][0]["title"], "Scavenger Hunt")

    def test_filter_by_category(self):
        resp = self.client.get("/activities/", {"category": str(self.cat.id)})
        data = json.loads(resp.content)
        self.assertEqual(data["count"], 2)

    def test_pagination(self):
        resp = self.client.get("/activities/", {"page": 1, "limit": 1})
        data = json.loads(resp.content)
        self.assertEqual(len(data["activities"]), 1)
        self.assertEqual(data["total"], 2)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["limit"], 1)

    def test_sort_by_title(self):
        resp = self.client.get("/activities/", {"sort": "title"})
        data = json.loads(resp.content)
        titles = [a["title"] for a in data["activities"]]
        self.assertEqual(titles, ["Scavenger Hunt", "Team Building"])

    def test_400_for_invalid_category(self):
        resp = self.client.get("/activities/", {"category": "not-a-number"})
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.content)
        self.assertEqual(data["status"], 400)
        self.assertIn("error", data)

    def test_anonymous_can_list_activities_json(self):
        self.client.logout()
        resp = self.client.get("/activities/")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data["total"], 2)


class ActivityDetailTests(TestCase):
    """Test GET /activities/<id>/ endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="faculty@test.edu",
            email="faculty@test.edu",
            password="testpass123",
        )
        self.client.login(username="faculty@test.edu", password="testpass123")
        self.activity = Activity.objects.create(
            title="Scavenger Hunt",
            description="Find items outside",
        )

    def test_detail_returns_activity(self):
        resp = self.client.get(f"/activities/{self.activity.slug}/")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data["title"], "Scavenger Hunt")
        self.assertEqual(data["slug"], "scavenger-hunt")
        self.assertEqual(data["description"], "Find items outside")
        self.assertIn("materials", data)

    def test_detail_404_for_invalid_slug(self):
        resp = self.client.get("/activities/non-existent-slug/")
        self.assertEqual(resp.status_code, 404)
        data = json.loads(resp.content)
        self.assertEqual(data["status"], 404)
        self.assertIn("error", data)

    def test_anonymous_can_view_detail_json(self):
        self.client.logout()
        resp = self.client.get(f"/activities/{self.activity.slug}/")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data["title"], "Scavenger Hunt")

    def test_anonymous_material_open_redirects_to_login(self):
        self.client.logout()
        resp = self.client.get("/activities/materials/99999/open/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp["Location"])

    def test_anonymous_material_download_redirects_to_login(self):
        self.client.logout()
        resp = self.client.get("/activities/materials/99999/download/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp["Location"])

    def test_anonymous_direct_media_url_redirects_to_login(self):
        """Uploaded files must not be world-readable via /media/ (bypasses material_open)."""
        self.client.logout()
        resp = self.client.get("/media/materials/2020/01/anything.pdf")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp["Location"])


class TagListTests(TestCase):
    """Test GET /tags/ endpoint."""

    def setUp(self):
        self.client = Client()
        Tag.objects.create(name="group")
        Tag.objects.create(name="homework")

    def test_tag_list_returns_all_tags(self):
        resp = self.client.get("/tags/")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data["tags"]), 2)
        names = [t["name"] for t in data["tags"]]
        self.assertIn("group", names)
        self.assertIn("homework", names)


class CategoryListTests(TestCase):
    """Test GET /categories/ endpoint."""

    def setUp(self):
        self.client = Client()
        Category.objects.create(name="Icebreakers", description="Get started")

    def test_category_list_returns_all_categories(self):
        resp = self.client.get("/categories/")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data["categories"]), 1)
        self.assertEqual(data["categories"][0]["name"], "Icebreakers")
