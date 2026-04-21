import json

from minio import Minio

s3_client = Minio(
    endpoint="localhost:9000",
    access_key="admin",
    secret_key="super_secret_pass",
    secure=False,
)

bucket_name = "menu-images"


def init_s3_bucket():
    if not s3_client.bucket_exists(bucket_name):
        s3_client.make_bucket(bucket_name)
        print(f"Бакет '{bucket_name}' успешно создан")
    else:
        print(f"Бакет '{bucket_name}' уже существует")

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
            }
        ],
    }

    s3_client.set_bucket_policy(bucket_name, json.dumps(policy))
    print(f"Публичный доступ для бакета '{bucket_name}' успешно настроен")


if __name__ == "__main__":
    init_s3_bucket()
