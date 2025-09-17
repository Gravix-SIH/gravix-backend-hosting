# serializers.py
from rest_framework import serializers
from .models import Assessment, Counselor, Booking, Resource

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ['id', 'type', 'responses', 'score', 'risk_level', 'created_at']
        read_only_fields = fields

class CounselorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Counselor
        fields = ['id', 'name', 'email', 'specializations', 'availability']

class BookingSerializer(serializers.ModelSerializer):
    counselor_id = serializers.PrimaryKeyRelatedField(
        queryset=Counselor.objects.all(),
        source="counselor"
    )

    class Meta:
        model = Booking
        fields = [
            'id',
            'counselor_id',
            'student', 'anon_id',
            'privacy_anonymous', 'status',
            'scheduled_time', 'notes'
        ]
        read_only_fields = ['id', 'student', 'anon_id', 'status']

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'title', 'description', 'category', 'link', 'created_at']
