import pytest
from rest_framework.test import APIClient
from users.models import User
from bookings.models import Booking
from resources.models import Resource
from assessments.models import Assessment
from django.utils import timezone
from datetime import timedelta
import uuid


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        email="admin@test.com",
        username="admin@test.com",
        password="testpass123",
        role="admin",
        name="Admin User",
    )
    return user


@pytest.fixture
def student_user(db):
    user = User.objects.create_user(
        email="student@test.com",
        username="student@test.com",
        password="testpass123",
        role="student",
        name="Student User",
    )
    return user


@pytest.fixture
def counsellor_user(db):
    user = User.objects.create_user(
        email="counsellor@test.com",
        username="counsellor@test.com",
        password="testpass123",
        role="counsellor",
        name="Counselor User",
        department="Mental Health",
    )
    return user


@pytest.fixture
def student_user2(db):
    user = User.objects.create_user(
        email="student2@test.com",
        username="student2@test.com",
        password="testpass123",
        role="student",
        name="Student Two",
    )
    return user


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def student_client(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    return api_client


@pytest.fixture
def sample_booking(db, student_user, counsellor_user):
    return Booking.objects.create(
        student=student_user,
        counsellor=counsellor_user,
        date=timezone.now().date() + timedelta(days=1),
        time="10:00",
        session_type="video",
        status="pending",
    )


@pytest.fixture
def sample_resource(db, admin_user):
    return Resource.objects.create(
        title="Test Resource",
        description="A test resource",
        type="article",
        url="https://example.com/resource",
        category="Mental Health",
        created_by=admin_user,
    )


@pytest.fixture
def sample_assessment(db, student_user):
    return Assessment.objects.create(
        user=student_user,
        assessment_type="phq9",
        score=5,
        max_score=27,
        severity="Minimal",
        answers=[0, 0, 1, 0, 0, 0, 0, 0, 0],
    )


# ─── Admin Stats ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestAdminStats:
    def test_admin_can_get_stats(self, admin_client):
        response = admin_client.get("/api/admin/stats/")
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "bookings" in data
        assert "resources" in data
        assert "assessments" in data
        assert data["users"]["total"] >= 1

    def test_non_admin_cannot_get_stats(self, student_client):
        response = student_client.get("/api/admin/stats/")
        assert response.status_code == 403


# ─── Admin Users ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestAdminUserList:
    def test_admin_can_list_users(self, admin_client, student_user):
        response = admin_client.get("/api/admin/users/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        emails = [u.get("email") for u in data if u.get("email")]
        assert "student@test.com" in emails

    def test_non_admin_cannot_list_users(self, student_client):
        response = student_client.get("/api/admin/users/")
        assert response.status_code == 403

    def test_admin_can_filter_by_role(self, admin_client, student_user, counsellor_user):
        response = admin_client.get("/api/admin/users/?role=student")
        assert response.status_code == 200
        data = response.json()
        for u in data:
            assert u["role"] == "student"

    def test_admin_can_search_users(self, admin_client, student_user):
        response = admin_client.get("/api/admin/users/?search=Student")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1


@pytest.mark.django_db
class TestAdminUserDetail:
    def test_admin_can_view_user(self, admin_client, student_user):
        response = admin_client.get(f"/api/admin/users/{student_user.id}/")
        assert response.status_code == 200
        assert response.json()["email"] == "student@test.com"

    def test_admin_can_update_user_role(self, admin_client, student_user):
        response = admin_client.patch(
            f"/api/admin/users/{student_user.id}/",
            {"role": "counsellor"},
            format="json",
        )
        assert response.status_code == 200
        student_user.refresh_from_db()
        assert student_user.role == "counsellor"

    def test_admin_can_deactivate_user(self, admin_client, student_user):
        response = admin_client.patch(
            f"/api/admin/users/{student_user.id}/",
            {"is_active": False},
            format="json",
        )
        assert response.status_code == 200
        student_user.refresh_from_db()
        assert student_user.is_active is False

    def test_admin_can_delete_user(self, admin_client, student_user):
        user_id = student_user.id
        response = admin_client.delete(f"/api/admin/users/{user_id}/")
        assert response.status_code == 204
        assert not User.objects.filter(id=user_id).exists()

    def test_non_admin_cannot_update_user(self, student_client, student_user2):
        response = student_client.patch(
            f"/api/admin/users/{student_user2.id}/",
            {"role": "admin"},
            format="json",
        )
        assert response.status_code == 403


# ─── Admin Bookings ────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestAdminBookingList:
    def test_admin_can_list_all_bookings(
        self, admin_client, sample_booking
    ):
        response = admin_client.get("/api/admin/bookings/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_non_admin_cannot_list_bookings(self, student_client, sample_booking):
        response = student_client.get("/api/admin/bookings/")
        assert response.status_code == 403

    def test_admin_can_filter_by_status(self, admin_client, sample_booking):
        response = admin_client.get("/api/admin/bookings/?status=pending")
        assert response.status_code == 200
        data = response.json()
        for b in data:
            assert b["status"] == "pending"


@pytest.mark.django_db
class TestAdminBookingDetail:
    def test_admin_can_update_booking_status(
        self, admin_client, sample_booking
    ):
        response = admin_client.patch(
            f"/api/admin/bookings/{sample_booking.id}/",
            {"status": "confirmed"},
            format="json",
        )
        assert response.status_code == 200
        sample_booking.refresh_from_db()
        assert sample_booking.status == "confirmed"


# ─── Admin Resources ───────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestAdminResourceListCreate:
    def test_admin_can_list_resources(self, admin_client, sample_resource):
        response = admin_client.get("/api/admin/resources/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_non_admin_cannot_create_resource(self, student_client):
        response = student_client.post(
            "/api/admin/resources/",
            {
                "title": "New Resource",
                "type": "article",
                "url": "https://example.com/new",
                "category": "Test",
            },
            format="json",
        )
        assert response.status_code == 403

    def test_admin_can_create_resource(self, admin_client):
        response = admin_client.post(
            "/api/admin/resources/",
            {
                "title": "New Resource",
                "type": "article",
                "url": "https://example.com/new",
                "category": "Test",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["title"] == "New Resource"


@pytest.mark.django_db
class TestAdminResourceDetail:
    def test_admin_can_update_resource(self, admin_client, sample_resource):
        response = admin_client.patch(
            f"/api/admin/resources/{sample_resource.id}/",
            {"title": "Updated Title"},
            format="json",
        )
        assert response.status_code == 200
        sample_resource.refresh_from_db()
        assert sample_resource.title == "Updated Title"

    def test_admin_can_delete_resource(self, admin_client, sample_resource):
        resource_id = sample_resource.id
        response = admin_client.delete(f"/api/admin/resources/{resource_id}/")
        assert response.status_code == 204
        assert not Resource.objects.filter(id=resource_id).exists()


# ─── Admin Assessments ──────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestAdminAssessmentStats:
    def test_admin_can_get_assessment_stats(self, admin_client, sample_assessment):
        response = admin_client.get("/api/admin/assessments/stats/")
        assert response.status_code == 200
        data = response.json()
        assert "total_submissions" in data
        assert "by_type" in data
        assert "average_scores" in data
        assert data["total_submissions"] >= 1

    def test_non_admin_cannot_get_stats(self, student_client):
        response = student_client.get("/api/admin/assessments/stats/")
        assert response.status_code == 403


@pytest.mark.django_db
class TestAdminAssessmentList:
    def test_admin_can_list_assessments(self, admin_client, sample_assessment):
        response = admin_client.get("/api/admin/assessments/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


# ─── Audit Logs ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestAuditLog:
    def test_admin_can_list_audit_logs(self, admin_client):
        response = admin_client.get("/api/admin/audit-logs/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_non_admin_cannot_list_audit_logs(self, student_client):
        response = student_client.get("/api/admin/audit-logs/")
        assert response.status_code == 403

    def test_audit_log_created_on_user_update(
        self, admin_client, student_user, admin_user
    ):
        admin_client.patch(
            f"/api/admin/users/{student_user.id}/",
            {"role": "counsellor"},
            format="json",
        )
        response = admin_client.get("/api/admin/audit-logs/")
        assert response.status_code == 200
        data = response.json()
        update_logs = [l for l in data if l["action"] == "update" and l["target_type"] == "User"]
        assert len(update_logs) >= 1

    def test_audit_log_created_on_user_delete(
        self, admin_client, student_user2
    ):
        user_id = student_user2.id
        admin_client.delete(f"/api/admin/users/{user_id}/")
        response = admin_client.get("/api/admin/audit-logs/")
        data = response.json()
        delete_logs = [l for l in data if l["action"] == "delete" and l["target_type"] == "User"]
        assert len(delete_logs) >= 1
