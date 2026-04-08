from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    counsellor_name = serializers.CharField(source='counsellor.name', read_only=True)
    counsellor_specialty = serializers.SerializerMethodField()
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_email = serializers.EmailField(source='student.email', read_only=True)
    meeting_details = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['id', 'student', 'counsellor', 'counsellor_name', 'counsellor_specialty',
                  'student_name', 'student_email', 'date', 'time', 'session_type', 'status', 'notes',
                  'meeting_link', 'meeting_phone', 'meeting_address', 'meeting_details',
                  'confirmed_at', 'created_at']
        read_only_fields = ['id', 'created_at', 'confirmed_at']

    def get_counsellor_specialty(self, obj):
        if obj.counsellor.department:
            return obj.counsellor.department
        return "General Counseling"

    def get_meeting_details(self, obj):
        return obj.get_meeting_details()


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['counsellor', 'date', 'time', 'session_type', 'notes']

    def validate_time(self, value):
        import re
        pattern = r'^([1-9]|1[0-2]):[0-5][0-9]\s*(AM|PM|am|pm)$'
        if not re.match(pattern, value.strip()):
            raise serializers.ValidationError(
                "Invalid time format. Use format like '9:00 AM' or '12:30 PM'"
            )
        return value.strip()

    def validate_session_type(self, value):
        valid_types = ['video', 'in-person', 'phone']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid session type. Must be one of: {', '.join(valid_types)}"
            )
        return value

    def validate_notes(self, value):
        if value and len(value) > 1000:
            raise serializers.ValidationError("Notes must be 1000 characters or less")
        return value

    def validate_date(self, value):
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("Cannot book a session for a past date")
        return value

    def validate(self, attrs):
        from datetime import date, datetime
        counsellor = attrs.get('counsellor')
        booking_date = attrs.get('date')
        booking_time = attrs.get('time')

        # Parse time string
        try:
            time_part = datetime.strptime(booking_time.strip(), "%I:%M %p").time()
        except ValueError:
            raise serializers.ValidationError({"time": "Invalid time format"})

        # Past time on today
        if booking_date == date.today():
            if time_part < datetime.now().time():
                raise serializers.ValidationError({"time": "Cannot book a time that has already passed today"})

        # Double-booking prevention
        existing = Booking.objects.filter(
            counsellor=counsellor,
            date=booking_date,
            time=booking_time.strip(),
            status__in=['pending', 'confirmed']
        ).exists()
        if existing:
            raise serializers.ValidationError({"time": "This time slot is already booked with this counselor"})

        return attrs

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)
