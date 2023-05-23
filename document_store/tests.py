from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Document, Folder, Topic
from .serializers import DocumentSerializer, FolderSerializer, TopicSerializer
from .pagination import StandardPagination


class TopicViewSetTestCase(TestCase):
    def setUp(self):
        self.topic1 = Topic.objects.create(name="Topic 1")
        self.topic2 = Topic.objects.create(name="Topic 2")
        self.valid_payload = {"name": "New Topic"}
        self.invalid_payload = {"name": ""}

    def test_create_topic_with_valid_payload(self):
        client = APIClient()
        url = reverse("topic-list")
        response = client.post(url, data=self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Topic.objects.count(), 3)

    def test_create_topic_with_invalid_payload(self):
        client = APIClient()
        url = reverse("topic-list")
        response = client.post(url, data=self.invalid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Topic.objects.count(), 2)

    def test_get_topics(self):
        client = APIClient()
        response = client.get(reverse("topic-list"))

        response.query_params = {}
        paginator = StandardPagination()
        topics = Topic.objects.all()
        paginated_topics = paginator.paginate_queryset(topics, request=response)
        serializer = TopicSerializer(paginated_topics, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results"), serializer.data)

    def test_get_topic(self):
        client = APIClient()
        url = reverse("topic-detail", args=[self.topic1.pk])
        response = client.get(url)

        topic = Topic.objects.get(pk=self.topic1.pk)
        serializer = TopicSerializer(topic)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class FolderViewSetTestCase(TestCase):
    def setUp(self):
        self.folder1 = Folder.objects.create(name="Folder 1")
        self.folder2 = Folder.objects.create(name="Folder 2")
        self.valid_payload = {"name": "New Folder"}
        self.invalid_payload = {"name": ""}

    def test_create_folder_with_valid_payload(self):
        client = APIClient()
        url = reverse("folder-list")

        response = client.post(url, data=self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Folder.objects.count(), 3)

    def test_create_folder_with_invalid_payload(self):
        client = APIClient()
        url = reverse("folder-list")

        response = client.post(url, data=self.invalid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Folder.objects.count(), 2)

    def test_get_folders(self):
        client = APIClient()
        response = client.get(reverse("folder-list"))

        folders = Folder.objects.all()
        serializer = FolderSerializer(folders, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_folder(self):
        client = APIClient()
        url = reverse("folder-detail", args=[self.folder1.pk])
        response = client.get(url)

        folder = Folder.objects.get(pk=self.folder1.pk)
        serializer = FolderSerializer(folder)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class DocumentViewSetTestCase(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(name="Topic")
        self.folder = Folder.objects.create(name="Folder")
        self.document1 = Document.objects.create(
            name="Document 1", folder=self.folder, topic=self.topic
        )
        self.document2 = Document.objects.create(
            name="Document 2", folder=self.folder, topic=self.topic
        )
        self.valid_payload = {
            "name": "New Document",
            "folder": self.folder.pk,
            "topic": self.topic.pk,
            "file": SimpleUploadedFile("temp.txt", b"file_content"),
        }
        self.invalid_payload = {"name": ""}

    def test_create_document_with_valid_payload(self):
        client = APIClient()
        url = reverse("document-list")
        response = client.post(url, data=self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 3)

    def test_create_document_with_invalid_payload(self):
        client = APIClient()
        url = reverse("document-list")
        response = client.post(url, data=self.invalid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Document.objects.count(), 2)

    def test_get_documents(self):
        client = APIClient()
        response = client.get(reverse("document-list"))

        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_documents_by_topic(self):
        client = APIClient()
        url = reverse("document-list")
        topic_name = "Topic"
        response = client.get(url, {"topic": topic_name})

        documents = Document.objects.filter(topic__name=topic_name)
        serializer = DocumentSerializer(documents, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_document(self):
        client = APIClient()
        url = reverse("document-detail", args=[self.document1.pk])
        response = client.get(url)

        document = Document.objects.get(pk=self.document1.pk)
        serializer = DocumentSerializer(document)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
