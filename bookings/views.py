from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer
from users.models import User


class BookingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Booking.objects.filter(student=user)
        elif user.role == 'counsellor':
            return Booking.objects.filter(counsellor=user)
        return Booking.objects.all()

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Booking.objects.filter(student=user)
        elif user.role == 'counsellor':
            return Booking.objects.filter(counsellor=user)
        return Booking.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status in ['completed', 'cancelled']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(f"Cannot cancel a {instance.status} session")
        instance.status = 'cancelled'
        instance.save()
        return Response({'status': 'cancelled'}, status=status.HTTP_200_OK)


class BookingConfirmView(generics.UpdateAPIView):
    """Counsellor confirms a booking and adds meeting details."""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Booking.objects.filter(counsellor=self.request.user)

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        if booking.status != 'pending':
            return Response(
                {'error': f'Cannot confirm a {booking.status} booking'},
                status=status.HTTP_400_BAD_REQUEST
            )

        meeting_link = request.data.get('meeting_link', '')
        meeting_phone = request.data.get('meeting_phone', '')
        meeting_address = request.data.get('meeting_address', '')

        # Validate meeting details based on session type
        session_type = booking.session_type
        if session_type == 'video' and not meeting_link:
            return Response({'error': 'Meeting link is required for video sessions'}, status=400)
        elif session_type == 'phone' and not meeting_phone:
            return Response({'error': 'Phone number is required for phone sessions'}, status=400)
        elif session_type == 'in-person' and not meeting_address:
            return Response({'error': 'Address is required for in-person sessions'}, status=400)

        from django.utils import timezone
        booking.meeting_link = meeting_link
        booking.meeting_phone = meeting_phone
        booking.meeting_address = meeting_address
        booking.status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.save()

        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class UpcomingBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from datetime import date
        return Booking.objects.filter(
            student=self.request.user,
            date__gte=date.today(),
            status__in=['pending', 'confirmed']
        ).order_by('date', 'time')


class CounselorListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        counselors = User.objects.filter(role='counsellor', is_active=True)
        data = []
        for c in counselors:
            data.append({
                'id': str(c.id),
                'name': c.name or c.email,
                'specialty': c.department or 'General Counseling',
                'experience': '5 years',
                'rating': 4.8,
                'reviews': 120,
                'languages': ['English'],
                'education': 'Certified Counselor',
                'next_available': 'Tomorrow, 10:00 AM',
                'session_types': ['video', 'in-person', 'phone'],
                'expertise': ['Stress Management', 'Student Counseling'],
                'bio': 'Experienced counselor dedicated to student mental health.'
            })
        return Response(data)


class CounselorSlotsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        counsellor_id = request.query_params.get('counsellor')
        date_str = request.query_params.get('date')
        if not counsellor_id or not date_str:
            return Response({'times': []})
        times = list(Booking.objects.filter(
            counsellor_id=counsellor_id,
            date=date_str,
            status__in=['pending', 'confirmed']
        ).values_list('time', flat=True))
        return Response({'times': times})
