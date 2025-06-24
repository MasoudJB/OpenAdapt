import os

API_URL = os.getenv("API_URL", "")
API_KEY = os.getenv("API_KEY", "")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
SUBTASK_ID = os.getenv("SUBTASK_ID", "")
SERVER_ID = os.getenv("SERVER_ID", "")

# screenshot saving directory
TMP_DIR = os.path.join(os.path.dirname(__file__), "tmp")
os.makedirs(TMP_DIR, exist_ok=True)
