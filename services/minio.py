import io
import uuid

from fastapi import Depends
from mako.parsetree import DefTag

from configs.Minio import base_bucket
from repositories.minio import MinioRepository
from schemas.minio import MinioContentType


class MinioService:
    def __init__(self, repo: MinioRepository = Depends()):
        self._repo = repo

    def upload_resume(self, id: uuid.UUID, pdf: bytes) -> str:
        return self._repo.create_object_from_byte(
            f"resume/{id}/{uuid.uuid4()}.pdf",
            io.BytesIO(pdf),
            MinioContentType.PDF,
        )

    def upload_video_card(self, id: uuid.UUID, video: bytes) -> str:
        return self._repo.create_object_from_byte(
            f"card/{id}/{uuid.uuid4()}.mp4", io.BytesIO(video), MinioContentType.MP4
        )

    def get_link(self, object_path: str, bucket_name: str = base_bucket) -> str:
        url = self._repo.get_link(object_path, bucket_name)

        return url
