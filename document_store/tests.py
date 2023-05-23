from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .cache_manager import CacheKeys
from .models import Document, Folder, Topic
from .pagination import StandardPagination
from .serializers import DocumentSerializer, FolderSerializer, TopicSerializer


class TopicViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a user and obtain an authentication token
        self.user = User.objects.create_user(
            username="test_user", password="test_password"
        )
        self.client.force_authenticate(user=self.user)

        self.topic1 = Topic.objects.create(name="Topic 1")
        self.topic2 = Topic.objects.create(name="Topic 2")
        self.valid_payload = {"name": "New Topic"}
        self.invalid_payload = {"name": ""}

    def tearDown(self):
        # Clear cache after each test
        cache.clear()

    def test_create_topic_with_valid_payload(self):
        url = reverse("topic-list")
        response = self.client.post(url, data=self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Topic.objects.count(), 3)

    def test_create_topic_with_invalid_payload(self):
        url = reverse("topic-list")
        response = self.client.post(url, data=self.invalid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Topic.objects.count(), 2)

    def test_get_topics(self):
        response = self.client.get(reverse("topic-list"))

        response.query_params = {}
        paginator = StandardPagination()
        topics = Topic.objects.all()
        paginated_topics = paginator.paginate_queryset(topics, request=response)
        serializer = TopicSerializer(paginated_topics, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results"), serializer.data)

    def test_get_topic(self):
        url = reverse("topic-detail", args=[self.topic1.pk])
        response = self.client.get(url)

        topic = Topic.objects.get(pk=self.topic1.pk)
        serializer = TopicSerializer(topic)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_topic_list_caching(self):
        # Make the first request
        response1 = self.client.get(reverse("topic-list"))
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data, cache.get(CacheKeys.TOPIC_LIST_KEY))

        # Update the topic and make a second request
        self.topic1.name = "Updated Topic"
        self.topic1.save()
        response2 = self.client.get(reverse("topic-list"))
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data, cache.get(CacheKeys.TOPIC_LIST_KEY))

        self.assertNotEqual(response1.data, response2.data)

    def test_topic_detail_caching(self):
        # Make the first request
        url = reverse("topic-detail", args=[self.topic1.pk])
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response1.data,
            cache.get(CacheKeys.TOPIC_DETAIL_KEY_PREFIX + str(self.topic1.pk)),
        )

        # Update the topic and make a second request
        self.topic1.name = "Updated Topic"
        self.topic1.save()
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response2.data,
            cache.get(CacheKeys.TOPIC_DETAIL_KEY_PREFIX + str(self.topic1.pk)),
        )

        self.assertNotEqual(response1.data, response2.data)


class FolderViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a user and obtain an authentication token
        self.user = User.objects.create_user(
            username="test_user", password="test_password"
        )
        self.client.force_authenticate(user=self.user)

        self.folder1 = Folder.objects.create(name="Folder 1")
        self.folder2 = Folder.objects.create(name="Folder 2")
        self.valid_payload = {"name": "New Folder"}
        self.invalid_payload = {"name": ""}

    def tearDown(self):
        # Clear cache after each test
        cache.clear()

    def test_create_folder_with_valid_payload(self):
        url = reverse("folder-list")

        response = self.client.post(url, data=self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Folder.objects.count(), 3)

    def test_create_folder_with_invalid_payload(self):
        url = reverse("folder-list")

        response = self.client.post(url, data=self.invalid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Folder.objects.count(), 2)

    def test_get_folders(self):
        response = self.client.get(reverse("folder-list"))

        folders = Folder.objects.all()
        response.query_params = {}
        paginator = StandardPagination()
        paginated_folders = paginator.paginate_queryset(folders, request=response)
        serializer = FolderSerializer(paginated_folders, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results"), serializer.data)

    def test_get_folder(self):
        url = reverse("folder-detail", args=[self.folder1.pk])
        response = self.client.get(url)

        folder = Folder.objects.get(pk=self.folder1.pk)
        serializer = FolderSerializer(folder)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_folder_list_caching(self):
        # Make the first request
        response1 = self.client.get(reverse("folder-list"))
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data, cache.get(CacheKeys.FOLDER_LIST_KEY))

        # Update the folder and make a second request
        self.folder1.name = "Updated Folder"
        self.folder1.save()
        response2 = self.client.get(reverse("folder-list"))
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data, cache.get(CacheKeys.FOLDER_LIST_KEY))

        self.assertNotEqual(response1.data, response2.data)


class DocumentViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a user and obtain an authentication token
        self.user = User.objects.create_user(
            username="test_user", password="test_password"
        )
        self.client.force_authenticate(user=self.user)

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

    def tearDown(self):
        # Clear cache after each test
        cache.clear()

    def test_create_document_with_valid_payload(self):
        url = reverse("document-list")
        response = self.client.post(url, data=self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 3)

    def test_create_document_with_invalid_payload(self):
        url = reverse("document-list")
        response = self.client.post(url, data=self.invalid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Document.objects.count(), 2)

    def test_get_documents(self):
        response = self.client.get(reverse("document-list"))

        documents = Document.objects.all()
        response.query_params = {}
        paginator = StandardPagination()
        paginated_documents = paginator.paginate_queryset(documents, request=response)
        serializer = DocumentSerializer(paginated_documents, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results"), serializer.data)

    def test_filter_documents_by_topic(self):
        url = reverse("document-list")
        topic_name = "Topic"
        response = self.client.get(url, {"topic": topic_name})

        documents = Document.objects.filter(topic__name=topic_name)
        response.query_params = {}
        paginator = StandardPagination()
        paginated_documents = paginator.paginate_queryset(documents, request=response)
        serializer = DocumentSerializer(paginated_documents, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results"), serializer.data)

    def test_get_document(self):
        url = reverse("document-detail", args=[self.document1.pk])
        response = self.client.get(url)

        document = Document.objects.get(pk=self.document1.pk)
        serializer = DocumentSerializer(document)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_document_list_caching(self):
        # Make the first request
        response1 = self.client.get(reverse("document-list"))
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data, cache.get(CacheKeys.DOCUMENT_LIST_KEY))

        # Update the doc and make a second request
        self.document1.name = "Updated document"
        self.document1.save()
        response2 = self.client.get(reverse("document-list"))
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data, cache.get(CacheKeys.DOCUMENT_LIST_KEY))

        self.assertNotEqual(response1.data, response2.data)

    def test_document_detail_caching(self):
        # Make the first request
        url = reverse("document-detail", args=[self.document1.pk])
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response1.data,
            cache.get(CacheKeys.DOCUMENT_DETAIL_KEY_PREFIX + str(self.document1.pk)),
        )

        # Update the document and make a second request
        self.document1.name = "Updated Document"
        self.document1.save()
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response2.data,
            cache.get(CacheKeys.DOCUMENT_DETAIL_KEY_PREFIX + str(self.document1.pk)),
        )

        self.assertNotEqual(response1.data, response2.data)
