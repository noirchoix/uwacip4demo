from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterator, Protocol


@dataclass(frozen=True)
class StoredObject:
    object_ref: str
    content_hash: str
    size_bytes: int
    content_type: str


class EvidenceStorePort(Protocol):
    async def put_bytes(
        self, *, data: bytes, content_type: str, suggested_name: str
    ) -> StoredObject: ...
    async def get_bytes(self, object_ref: str) -> bytes: ...
