from __future__ import annotations

import asyncio
import hashlib
from uuid import uuid4

import boto3

from pipe4.ports.evidence_store import StoredObject


class S3EvidenceStore:
    def __init__(
        self,
        *,
        bucket: str,
        endpoint_url: str | None,
        access_key_id: str | None,
        secret_access_key: str | None,
    ) -> None:
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )

    async def put_bytes(self, *, data: bytes, content_type: str, suggested_name: str) -> StoredObject:
        digest = hashlib.sha256(data).hexdigest()
        key = f"pipe4/evidence/{digest[:2]}/{digest}-{uuid4().hex}"
        await asyncio.to_thread(
            self.client.put_object,
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
            Metadata={"sha256": digest, "original-name": suggested_name[:200]},
        )
        return StoredObject(
            object_ref=f"s3://{self.bucket}/{key}",
            content_hash=digest,
            size_bytes=len(data),
            content_type=content_type,
        )

    async def get_bytes(self, object_ref: str) -> bytes:
        prefix = f"s3://{self.bucket}/"
        if not object_ref.startswith(prefix):
            raise ValueError("evidence reference is outside configured bucket")
        key = object_ref.removeprefix(prefix)
        response = await asyncio.to_thread(self.client.get_object, Bucket=self.bucket, Key=key)
        return await asyncio.to_thread(response["Body"].read)
