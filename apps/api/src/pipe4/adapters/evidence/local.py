from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import uuid4

import aiofiles

from pipe4.ports.evidence_store import StoredObject


class LocalEvidenceStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    async def put_bytes(self, *, data: bytes, content_type: str, suggested_name: str) -> StoredObject:
        digest = hashlib.sha256(data).hexdigest()
        safe_suffix = Path(suggested_name).suffix[:16]
        name = f"{digest[:16]}-{uuid4().hex}{safe_suffix}"
        path = self.root / name
        async with aiofiles.open(path, "wb") as handle:
            await handle.write(data)
        return StoredObject(
            object_ref=f"local://{name}",
            content_hash=digest,
            size_bytes=len(data),
            content_type=content_type,
        )

    async def get_bytes(self, object_ref: str) -> bytes:
        if not object_ref.startswith("local://"):
            raise ValueError("unsupported local evidence reference")
        async with aiofiles.open(self.root / object_ref.removeprefix("local://"), "rb") as handle:
            return await handle.read()
