# app/aws/s3.py
import os
import uuid
import mimetypes
import boto3
from botocore.config import Config
from werkzeug.utils import secure_filename

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

_aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
_aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

_boto_cfg = Config(
    region_name=AWS_REGION,
    retries={"max_attempts": 5, "mode": "standard"},
    connect_timeout=5,
    read_timeout=30,
)

s3_client = boto3.client(
    "s3",
    config=_boto_cfg,
    aws_access_key_id=_aws_access_key_id,
    aws_secret_access_key=_aws_secret_access_key,
)

s3_resource = boto3.resource(
    "s3",
    config=_boto_cfg,
    aws_access_key_id=_aws_access_key_id,
    aws_secret_access_key=_aws_secret_access_key,
)


def s3_bucket():
    """Returns a bucket object you can interact with"""
    if not S3_BUCKET:
        raise RuntimeError("S3_BUCKET is not set")
    return s3_resource.Bucket(S3_BUCKET)


def object_url(key: str) -> str:
    """Builds a public URL for an S3 object"""
    return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"


def _guess_content_type(
    filename: str, fallback: str = "application/octet-stream"
) -> str:
    """Guess the content type of a file based on its filename extension."""
    ctype, _ = mimetypes.guess_type(filename)
    return ctype or fallback


def upload_fileobj_private(file_storage, *, prefix: str = "avatars/") -> dict:
    """Upload a file to S3 without ACLs (bucket must have Object Ownership enforced)."""
    if not S3_BUCKET:
        raise RuntimeError("S3_BUCKET is not set")

    raw_name = secure_filename(file_storage.filename or f"upload-{uuid.uuid4()}")
    unique_key = f"{prefix}{uuid.uuid4()}-{raw_name}"
    content_type = file_storage.mimetype or _guess_content_type(raw_name)

    s3_client.upload_fileobj(
        Fileobj=file_storage,
        Bucket=S3_BUCKET,
        Key=unique_key,
        ExtraArgs={
            "ContentType": content_type,
            "CacheControl": "public, max-age=31536000",
        },
    )
    return {"key": unique_key}  # just return key; URL is presigned separately


def presigned_get_url(key: str, expires_in: int = 3600) -> str:
    """Generate a temporary URL to access a private S3 object."""
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=expires_in,
    )
