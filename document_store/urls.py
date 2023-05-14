from rest_framework.routers import DefaultRouter

from .views import TopicViewSet, FolderViewSet, DocumentViewSet

router = DefaultRouter()

router.register(r"topics", TopicViewSet, basename="topic")
router.register(r"documents", DocumentViewSet, basename="document")
router.register(r"folders", FolderViewSet, basename="folder")

urlpatterns = router.urls
