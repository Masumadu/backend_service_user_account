from blinker import Namespace

from .notification_handler import NotificationHandler


class Notifier:
    notification_signals: Namespace = Namespace()
    signal = notification_signals.signal("notify")

    def notify(self, notification_listener: NotificationHandler) -> None:
        """
        Notify the notification listener.

        :param notification_listener: The notification listener to be notified.
        :type notification_listener: NotificationHandler
        """
        self.signal.send(self, notification=notification_listener)

    @signal.connect
    def send_notification(self, **kwargs) -> None:
        """
        Send a notification.

        This method is connected to the 'notify' signal and is triggered
        when a notification is sent. It retrieves the notification from
        the keyword arguments and invokes the 'send' method on it.

        :param kwargs: Keyword arguments passed to the signal.
        """
        notification = kwargs["notification"]
        notification.send()
