from __future__ import annotations

"""Helpers for saving recordings to DynamoDB via REST API."""

import json
from typing import Any

import requests

from openadapt import utils
from openadapt.config import config
from openadapt.custom_logger import logger
from openadapt.db import crud
from openadapt.models import Recording


def save_recording_to_dynamo(recording: Recording) -> None:
    """Save a recording to DynamoDB through a REST API."""
    if not config.DYNAMODB_ENABLED:
        return

    if not config.DYNAMODB_API_URL:
        logger.warning("DynamoDB API URL not configured")
        return

    with crud.get_new_session(read_only=True) as session:
        action_events = crud.get_action_events(session, recording)

    action_dicts = utils.rows2dicts(action_events)
    payload: dict[str, Any] = {
        "recording_ID": str(recording.id),
        "steps": action_dicts,
    }

    headers = {"Content-Type": "application/json"}
    if config.DYNAMODB_API_KEY:
        headers["x-api-key"] = config.DYNAMODB_API_KEY

    try:
        response = requests.post(
            config.DYNAMODB_API_URL,
            data=json.dumps(payload),
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        logger.info(
            f"Saved recording {recording.id} to DynamoDB via {config.DYNAMODB_API_URL}"
        )
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Failed to save recording {recording.id} to DynamoDB: {exc}")
