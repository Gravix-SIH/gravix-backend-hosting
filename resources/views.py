from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Resource, ResourceBookmark
from .serializers import ResourceSerializer, ResourceBookmarkSerializer


class ResourceListView(generics.ListAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Resource.objects.all()
        category = self.request.query_params.get('category')
        if category and category != 'all':
            queryset = queryset.filter(category__iexact=category)
        return queryset


class ResourceBookmarkListView(generics.ListAPIView):
    serializer_class = ResourceBookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ResourceBookmark.objects.filter(user=self.request.user).select_related('resource')


class BookmarkResourceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, resource_id):
        try:
            resource = Resource.objects.get(id=resource_id)
            bookmark, created = ResourceBookmark.objects.get_or_create(
                user=request.user,
                resource=resource
            )
            if created:
                return Response({'status': 'bookmarked'}, status=201)
            return Response({'status': 'already bookmarked'})
        except Resource.DoesNotExist:
            return Response({'error': 'Resource not found'}, status=404)

    def delete(self, request, resource_id):
        try:
            bookmark = ResourceBookmark.objects.get(user=request.user, resource_id=resource_id)
            bookmark.delete()
            return Response({'status': 'removed'})
        except ResourceBookmark.DoesNotExist:
            return Response({'error': 'Bookmark not found'}, status=404)
