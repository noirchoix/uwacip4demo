import logging


class LoggingNotificationAdapter:
    async def notify(self, *, subject: str, event_type: str, payload: dict) -> None:
        logging.getLogger(__name__).info(
            "notification handoff", extra={"event_type": event_type, "aggregate_id": subject}
        )
