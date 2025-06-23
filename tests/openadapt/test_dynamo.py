"""Tests for DynamoDB integration."""

from unittest.mock import patch

from openadapt.models import Recording
from openadapt.record import finalize_recording
from openadapt.config import config


def test_finalize_recording_triggers_dynamo() -> None:
    """Ensure finalize_recording calls save_recording_to_dynamo when enabled."""
    recording = Recording(id=1)
    config.DYNAMODB_ENABLED = True
    with patch("openadapt.record.crud.post_process_events") as mock_post, patch(
        "openadapt.record.dynamo.save_recording_to_dynamo"
    ) as mock_save:
        finalize_recording(recording)
        mock_post.assert_called_once()
        mock_save.assert_called_once_with(recording)
