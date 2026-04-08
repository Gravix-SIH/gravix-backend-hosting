from django.urls import path
from .views import ResourceListView, ResourceBookmarkListView, BookmarkResourceView

urlpatterns = [
    path('', ResourceListView.as_view(), name='resource-list'),
    path('bookmarks/', ResourceBookmarkListView.as_view(), name='resource-bookmarks'),
    path('<uuid:resource_id>/bookmark/', BookmarkResourceView.as_view(), name='resource-bookmark'),
]
