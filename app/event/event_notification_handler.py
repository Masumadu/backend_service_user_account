from app.core.notifications import NotificationHandler


class EventNotificationHandler(NotificationHandler):
    """
    Event Notification handler.

    This class handles event notification. It publishes an Event message to
    the message queue which is consumed by the rightful service.
    """

    def send(self) -> None:
        """
        Send the event notification.

        This method publishes an Event message to the message queue for consumption
        by the appropriate service.
        """
