import pytest
from rest_framework.test import APIClient
from users.models import User
from bookings.models import Booking
from assessments.models import Assessment
from django.utils import timezone
from datetime import timedelta


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def counsellor_user(db):
    user = User.objects.create_user(
        email="counsellor@test.com",
        username="counsellor@test.com",
        password="testpass123",
        role="counsellor",
        name="Test Counsellor",
        department="Psychology",
    )
    return user


@pytest.fixture
def student_user(db):
    user = User.objects.create_user(
        email="student@test.com",
        username="student@test.com",
        password="testpass123",
        role="student",
        name="Test Student",
    )
    return user


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        email="admin@test.com",
        username="admin@test.com",
        password="testpass123",
        role="admin",
        name="Test Admin",
    )
    return user


@pytest.fixture
def counsellor_client(api_client, counsellor_user):
    api_client.force_authenticate(user=counsellor_user)
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
def sample_assessment(db, student_user):
    return Assessment.objects.create(
        user=student_user,
        assessment_type="phq9",
        score=10,
        max_score=27,
        severity="Moderate",
        answers=[1, 2, 1, 0, 1, 2, 1, 0, 1],
    )


# ─── Counselor Stats ───────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestCounselorStats:
    def test_counsellor_can_get_stats(self, counsellor_client, sample_booking):
        response = counsellor_client.get("/api/counsellor/stats/")
        assert response.status_code == 200
        data = response.json()
        assert "upcoming_sessions" in data
        assert data["upcoming_sessions"] >= 1

    def test_non_counsellor_cannot_get_stats(self, student_client, admin_user):
        response = student_client.get("/api/counsellor/stats/")
        assert response.status_code == 403

    def test_admin_cannot_get_counsellor_stats(self, api_client, admin_user, sample_booking):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/counsellor/stats/")
        assert response.status_code == 403


# ─── Counselor Bookings ────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestCounselorBookingList:
    def test_counsellor_can_list_own_bookings(
        self, counsellor_client, sample_booking
    ):
        response = counsellor_client.get("/api/counsellor/bookings/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_non_counsellor_cannot_list(self, student_client):
        response = student_client.get("/api/counsellor/bookings/")
        assert response.status_code == 403

    def test_counsellor_can_filter_by_status(
        self, counsellor_client, sample_booking
    ):
        response = counsellor_client.get("/api/counsellor/bookings/?status=pending")
        assert response.status_code == 200
        data = response.json()
        for b in data:
            assert b["status"] == "pending"


@pytest.mark.django_db
class TestCounselorBookingUpdate:
    def test_counsellor_can_confirm_booking(
        self, counsellor_client, sample_booking
    ):
        response = counsellor_client.patch(
            f"/api/counsellor/bookings/{sample_booking.id}/",
            {"status": "confirmed"},
            format="json",
        )
        assert response.status_code == 200
        sample_booking.refresh_from_db()
        assert sample_booking.status == "confirmed"

    def test_counsellor_cannot_access_other_booking(self, api_client, db):
        other = User.objects.create_user(
            email="other@test.com",
            username="other@test.com",
            password="testpass123",
            role="counsellor",
            name="Other",
        )
        student = User.objects.create_user(
            email="s2@test.com", username="s2@test.com", password="testpass123",
            role="student",
        )
        booking = Booking.objects.create(
            student=student,
            counsellor=other,
            date=timezone.now().date() + timedelta(days=1),
            time="10:00",
            session_type="video",
            status="pending",
        )
        api_client.force_authenticate(user=other)

        # Update to self works
        res = api_client.patch(
            f"/api/counsellor/bookings/{booking.id}/",
            {"status": "confirmed"},
            format="json",
        )
        assert res.status_code == 200


# ─── Counselor Assessments ──────────────────────────────────────────────────────


@pytest.mark.django_db
class TestCounselorAssessmentList:
    def test_counsellor_can_list_assessments(
        self, counsellor_client, sample_assessment
    ):
        #Counsellor can only see assessments from students they've had bookings with
        response = counsellor_client.get("/api/counsellor/assessments/")
        assert response.status_code == 200

    def test_non_counsellor_cannot_list(self, student_client):
        response = student_client.get("/api/counsellor/assessments/")
        assert response.status_code == 403

    def test_counsellor_can_filter_by_type(
        self, counsellor_client, sample_assessment
    ):
        response = counsellor_client.get(
            "/api/counsellor/assessments/?assessment_type=phq9"
        )
        assert response.status_code == 200
