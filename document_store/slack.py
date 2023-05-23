from django.conf import settings
from rest_framework import status

from slack import WebhookClient


def notify_slack_on_upload(document):
    client = WebhookClient(settings.SLACK_WEBHOOK_URL)

    message = (
        f"New document uploaded:\n\n"
        f"Name: {document.name}\n"
        f"Folder: {document.folder}\n"
        f"Topic: {document.topic}\n"
    )

    response = client.send(text=message)

    if not response.status_code == status.HTTP_200_OK:
        # TODO: Handle error case if Slack notification fails
        pass
