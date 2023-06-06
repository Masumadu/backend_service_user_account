from typing import Dict, List

from app.core.notifications import NotificationHandler
from app.producer import publish_to_kafka
from config import settings


class EmailNotificationHandler(NotificationHandler):
    """
    Email Notification handler.

    This class handles email notification. It publishes a NOTIFICATION message to
    the Kafka broker which is consumed by the notification service.

    :param recipients: The recipient(s) email address(es).
    :type recipients: List[str]
    :param details: Placeholders to be substituted by the notification service.
    :type details: Dict[str, str]
    :param meta: The metadata of the notification to be sent. Based on the specified,
        the message may be modified by the notification service.
        Check out url_notification for more info.
    :type meta: Dict[str, str]
    """

    def __init__(
        self, recipients: List[str], details: Dict[str, str], meta: Dict[str, str]
    ):
        self.recipients: list = recipients
        self.details: dict = details
        self.meta: dict = meta
        self.service_name: str = settings.app_id

    def send(self) -> None:
        """
        Send the email notification.
        """
        data = {
            "service_name": self.service_name,
            "meta": self.meta,
            "details": self.details,
            "recipients": self.recipients,
        }

        publish_to_kafka("EMAIL_NOTIFICATION", data)
