from rest_framework import serializers
from .models import Resource, ResourceBookmark


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'title', 'description', 'type', 'url', 'category', 'duration', 'rating', 'created_at']
        read_only_fields = ['id', 'created_at']


class ResourceBookmarkSerializer(serializers.ModelSerializer):
    resource = ResourceSerializer(read_only=True)

    class Meta:
        model = ResourceBookmark
        fields = ['id', 'resource', 'created_at']
        read_only_fields = ['id', 'created_at']
