from app.core.service_interfaces import EventHandlerInterface


class EventSubscriptionHandler(EventHandlerInterface):
    """
    Event Subscription handler.

    This class implements the EventHandlerInterface and provides an implementation
    for the event_handler method.
    """

    def handler(self, event_data: dict) -> None:
        """
        Handle the event.

        This method is called when an event occurs. It receives the event data and
        performs the necessary actions.

        :param event_data: Data associated with the event.
        """
