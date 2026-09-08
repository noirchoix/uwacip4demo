from __future__ import annotations

from typing import Protocol


class NotificationPort(Protocol):
    async def notify(
        self,
        *,
        subject: str,
        event_type: str,
        payload: dict[str, str | int | float | bool | None],
    ) -> None: ...
