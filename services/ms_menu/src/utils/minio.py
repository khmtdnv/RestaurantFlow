from config import settings
from minio import Minio

bucket_name = "menu-images"

_s3_client = Minio(
    endpoint=settings.MINIO_URL,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False,
)


def get_s3_client() -> Minio:
    return _s3_client
