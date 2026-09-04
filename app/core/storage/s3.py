from typing import BinaryIO

import aioboto3

from app.core.storage.interface import StorageService


class S3StorageService(StorageService):

    def __init__(
        self,
        *,
        bucket_name: str,
        region_name: str,
        endpoint_url: str | None = None,
        public_base_url: str | None = None,
    ) -> None:
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.endpoint_url = endpoint_url
        self.public_base_url = public_base_url

        self.session = aioboto3.Session()

    async def upload(
        self,
        *,
        file: BinaryIO,
        path: str,
        content_type: str,
    ) -> str:

        async with self.session.client(
            "s3",
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
        ) as client:

            await client.upload_fileobj(
                file,
                self.bucket_name,
                path,
                ExtraArgs={
                    "ContentType": content_type,
                },
            )

        return path

    async def delete(self, *, path: str) -> None:

        async with self.session.client(
            "s3",
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
        ) as client:

            await client.delete_object(
                Bucket=self.bucket_name,
                Key=path,
            )

    def get_url(self, *, path: str) -> str:

        if self.public_base_url:
            return f"{self.public_base_url.rstrip('/')}/{path}"

        return (
            f"https://{self.bucket_name}.s3."
            f"{self.region_name}.amazonaws.com/{path}"
        )
