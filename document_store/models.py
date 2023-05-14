from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Folder(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_folders",
    )

    def __str__(self):
        name = self.name
        if not self.parent:
            return name

        temp = self.parent
        while temp:
            name = f"{temp.name}/{name}"
            temp = temp.parent
        return name


class Document(models.Model):
    name = models.CharField(max_length=200)
    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, related_name="documents"
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="documents",
    )
    file = models.FileField(upload_to="documents/")

    def __str__(self):
        return f"{self.folder}/{self.name}"
