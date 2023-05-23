from rest_framework import serializers

from .models import Document, Folder, Topic


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


class FolderSerializer(serializers.ModelSerializer):
    children = (
        serializers.SerializerMethodField()
    )  # consists of files and nested folders

    def get_children(self, instance):
        children = [
            {"name": child.name, "type": "folder"}
            for child in instance.child_folders.all()
        ]
        children += [
            {"name": document.name, "type": "document"}
            for document in instance.documents.all()
        ]
        return children

    class Meta:
        model = Folder
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"
