from rest_framework import serializers
from users.models import User
from bookings.models import Booking
from resources.models import Resource
from assessments.models import Assessment


class AdminUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "name", "email", "department", "role",
            "is_anonymous", "anon_id", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "anon_id", "created_at", "updated_at"]

    def get_name(self, obj):
        if obj.is_anonymous:
            return obj.anon_id
        return obj.name

    def get_email(self, obj):
        if obj.is_anonymous:
            return ""
        return obj.email


class AdminBookingSerializer(serializers.ModelSerializer):
    counsellor_name = serializers.CharField(source="counsellor.name", read_only=True)
    counsellor_specialty = serializers.SerializerMethodField()
    student_name = serializers.CharField(source="student.name", read_only=True)
    student_email = serializers.CharField(source="student.email", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "student", "student_name", "student_email",
            "counsellor", "counsellor_name", "counsellor_specialty",
            "date", "time", "session_type", "status", "notes", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_counsellor_specialty(self, obj):
        if obj.counsellor.department:
            return obj.counsellor.department
        return "General Counseling"


class AdminResourceSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)

    class Meta:
        model = Resource
        fields = [
            "id", "title", "description", "type", "url",
            "category", "duration", "rating", "created_at", "created_by", "created_by_name",
        ]
        read_only_fields = ["id", "created_at"]


class AdminAssessmentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = [
            "id", "user", "user_name", "user_email",
            "assessment_type", "score", "max_score",
            "severity", "answers", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_user_name(self, obj):
        if obj.user.is_anonymous:
            return obj.user.anon_id
        return obj.user.name

    def get_user_email(self, obj):
        if obj.user.is_anonymous:
            return ""
        return obj.user.email
