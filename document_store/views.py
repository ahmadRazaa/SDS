from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework import viewsets
from rest_framework.response import Response

from .cache_manager import CacheKeys
from .models import Document, Folder, Topic
from .pagination import StandardPagination
from .serializers import FolderSerializer, TopicSerializer, DocumentSerializer


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    pagination_class = StandardPagination
    permission_classes = []

    def list(self, request, *args, **kwargs):
        cached_data = cache.get(CacheKeys.TOPIC_LIST_KEY)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(CacheKeys.TOPIC_LIST_KEY, response.data)
        return response

    def retrieve(self, request, *args, **kwargs):
        cache_key = CacheKeys.TOPIC_DETAIL_KEY_PREFIX + kwargs["pk"]
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data)
        return response


class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    pagination_class = StandardPagination
    permission_classes = []


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    pagination_class = StandardPagination
    permission_classes = []

    def get_queryset(self):
        queryset = Document.objects.select_related("topic", "folder").all()
        topic = self.request.query_params.get("topic")

        if topic is not None:
            queryset = queryset.filter(topic__name=topic)

        return queryset


@receiver([post_save, post_delete], sender=Topic)
@receiver([post_save, post_delete], sender=Folder)
@receiver([post_save, post_delete], sender=Document)
def invalidate_cache(sender, instance, **kwargs):
    cache.delete(CacheKeys.TOPIC_LIST_KEY)
    cache.delete(CacheKeys.TOPIC_DETAIL_KEY_PREFIX + str(instance.pk))
    cache.delete(CacheKeys.FOLDER_LIST_KEY)
    cache.delete(CacheKeys.FOLDER_DETAIL_KEY_PREFIX + str(instance.pk))
    cache.delete(CacheKeys.DOCUMENT_LIST_KEY)
    cache.delete(CacheKeys.DOCUMENT_DETAIL_KEY_PREFIX + str(instance.pk))
