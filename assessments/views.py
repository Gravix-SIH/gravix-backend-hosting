# views.py
from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Assessment, Counselor, Booking, Resource
from .serializers import AssessmentSerializer, CounselorSerializer, BookingSerializer, ResourceSerializer

class AssessmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('userId')
        if self.request.user.role in ['counselor', 'admin'] and user_id:
            return Assessment.objects.filter(user__id=user_id).order_by('-created_at')
        return Assessment.objects.filter(user=self.request.user).order_by('-created_at')


    def perform_create(self, serializer):
        responses = self.request.data.get('responses', {})
        type = self.request.data.get('type', {})
        score = sum(responses.values())
        risk_level = self.get_risk_level(score)
        serializer.save(
            user=self.request.user,
            type=type,
            responses=responses,
            score=score,
            risk_level=risk_level
        )

    def get_risk_level(self, score):
        if score <= 4:
            return 'minimal'
        if score <= 9:
            return 'mild'
        if score <= 14:
            return 'moderate'
        return 'severe'


class CounselorListView(generics.ListAPIView):
    serializer_class = CounselorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Counselor.objects.all()
        return qs


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('userId')
        if self.request.user.role in ['admin', 'counselor'] and user_id:
            return Booking.objects.filter(student__id=user_id)
        return Booking.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        anonymous = self.request.data.get('privacy_anonymous', False)
        if anonymous:
            serializer.save(student=None, anon_id=self.request.user.anon_id, privacy_anonymous=True)
        else:
            serializer.save(student=self.request.user, anon_id=None, privacy_anonymous=False)


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.all()

    def get_object(self):
        booking = super().get_object()
        if booking.student != self.request.user and self.request.user.role not in ['admin', 'counselor']:
            raise permissions.PermissionDenied("Not authorized to access this booking.")
        return booking

    def delete(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.status = 'cancelled'
        booking.save()
        return Response({"detail": "Booking cancelled successfully."}, status=200)


class ResourceListView(generics.ListAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category = self.request.query_params.get('category')
        qs = Resource.objects.all()
        if category:
            qs = qs.filter(category=category)
        return qs
