from typing import Literal

import aioboto3
from botocore.client import Config
from types_aiobotocore_s3.client import S3Client

from src.core.domain.value_object import ValueObject


class S3BucketOptions(ValueObject):
    url: str
    access_key: str
    secret_key: str
    bucket: str
    region: str | None = None
    addressing_style: Literal["virtual", "path"] = (
        "virtual"  # path is deprecated for AWS S3
    )


class S3BucketProvider:
    def __init__(self, options: S3BucketOptions):
        self.options = options

    async def connect(self) -> None:
        assert aioboto3 is not None
        self._session = aioboto3.Session()
        self._client = await self._session.client(
            "s3",
            endpoint_url=self.options.url,
            aws_access_key_id=self.options.access_key,
            aws_secret_access_key=self.options.secret_key,
            region_name=self.options.region,
            config=Config(
                s3={"addressing_style": self.options.addressing_style},
                signature_version="s3v4",  # for minio
                retries={
                    "max_attempts": 4,  # 1 try and up to 3 retries
                    "mode": "adaptive",
                },
            ),
            use_ssl=self.options.url.startswith("https"),
        ).__aenter__()

    async def disconnect(self) -> None:
        await self._client.close()

    @property
    def bucket(self) -> str:
        return self.options.bucket

    @property
    def client(self) -> "S3Client":
        return self._client
