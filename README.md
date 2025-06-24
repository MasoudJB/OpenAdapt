# recordingAgent

Simple Python tool to record mouse and keyboard events, upload screenshots to AWS S3, and send event data to a REST API (e.g. backed by DynamoDB).

## Usage

Set the following environment variables:

- `API_URL` – endpoint to receive event JSON
- `API_KEY` – optional API key header
- `S3_BUCKET_NAME` – S3 bucket for screenshots
- `AWS_ACCESS_KEY` and `AWS_SECRET_KEY` – credentials for S3
- `SUBTASK_ID` and `SERVER_ID` – identifiers included with each event

Install dependencies (requires Python 3.10+):

```bash
pip install -r requirements.txt
```

Run the recorder:

```bash
python -m recordingAgent.record
```

Press **ESC** to stop recording. Middle mouse click will also exit.
