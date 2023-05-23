from rest_framework import viewsets

from .models import Document, Folder, Topic
from .pagination import StandardPagination
from .serializers import FolderSerializer, TopicSerializer, DocumentSerializer


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    pagination_class = StandardPagination
    permission_classes = []


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
