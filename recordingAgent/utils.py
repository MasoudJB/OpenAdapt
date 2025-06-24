import os
import uuid
from typing import Optional

import boto3
from PIL import Image
import mss

from . import config


def take_screenshot(path: str) -> None:
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img.save(path)


def upload_to_s3(file_path: str) -> Optional[str]:
    try:
        if not all([config.S3_BUCKET_NAME, config.AWS_ACCESS_KEY, config.AWS_SECRET_KEY]):
            print("AWS credentials or bucket name missing.")
            return None

        s3 = boto3.client(
            "s3",
            aws_access_key_id=config.AWS_ACCESS_KEY,
            aws_secret_access_key=config.AWS_SECRET_KEY,
        )
        file_name = os.path.basename(file_path)
        s3.upload_file(file_path, config.S3_BUCKET_NAME, file_name, ExtraArgs={"ACL": "public-read"})
        public_url = f"https://{config.S3_BUCKET_NAME}.s3.amazonaws.com/{file_name}"
        return public_url
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None


def get_window_title() -> str:
    try:
        import pygetwindow
        win = pygetwindow.getActiveWindow()
        return win.title if win else ""
    except Exception:
        return ""
