from typing import Dict, List

from app.core.notifications import NotificationHandler
from app.producer import publish_to_kafka
from config import settings


class SMSNotificationHandler(NotificationHandler):
    """
    SMS Notification handler.

    This class handles SMS notification. It publishes a NOTIFICATION message to
    the Kafka broker which is consumed by the notification service.

    :param recipients: The recipient phone number(s).
    :type recipients: List[str]
    :param details: The details of the message you want to send.
    :type details: Dict[str, str]
    :param meta: The type of message you want to send. Based on the meta specified,
        the message may be modified by the notification service.
        Check out url_str for more info.
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
        Send the SMS notification.
        """
        data = {
            "service_name": self.service_name,
            "meta": self.meta,
            "details": self.details,
            "recipients": self.recipients,
        }

        publish_to_kafka("SMS_NOTIFICATION", data)
