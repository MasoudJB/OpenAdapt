import os
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Optional

import requests
from pynput import keyboard, mouse

from . import utils, config


@dataclass
class Event:
    id: str
    timestamp: float
    event_type: str
    x: Optional[int] = None
    y: Optional[int] = None
    screenshot_url: Optional[str] = None
    element_text: str = ""
    element_type: str = ""
    window_title: str = ""
    element_properties: dict | None = None
    subtask_id: str = config.SUBTASK_ID
    server_id: str = config.SERVER_ID


def send_event(event: Event) -> None:
    if not config.API_URL:
        print("API_URL not configured")
        return
    headers = {"x-api-key": config.API_KEY} if config.API_KEY else {}
    try:
        requests.post(config.API_URL, json=asdict(event), headers=headers, timeout=5)
    except Exception as e:
        print(f"Failed to send event: {e}")


running = True


def on_click(x, y, button, pressed):
    global running
    if not pressed:
        return
    if button == mouse.Button.middle:
        running = False
        return False
    path = os.path.join(config.TMP_DIR, f"{uuid.uuid4()}.png")
    utils.take_screenshot(path)
    url = utils.upload_to_s3(path)
    os.remove(path)
    evt = Event(
        id=str(uuid.uuid4()),
        timestamp=time.time(),
        event_type="click",
        x=x,
        y=y,
        screenshot_url=url,
        element_type=str(button),
        window_title=utils.get_window_title(),
        element_properties={},
    )
    send_event(evt)


def on_press(key):
    global running
    if key == keyboard.Key.esc:
        running = False
        return False
    try:
        key_str = key.char
    except AttributeError:
        key_str = str(key)
    evt = Event(
        id=str(uuid.uuid4()),
        timestamp=time.time(),
        event_type="key",
        element_text=key_str,
        window_title=utils.get_window_title(),
        element_properties={},
    )
    send_event(evt)


def run() -> None:
    with keyboard.Listener(on_press=on_press) as k_listener, \
            mouse.Listener(on_click=on_click) as m_listener:
        while running:
            time.sleep(0.1)
        k_listener.stop()
        m_listener.stop()


if __name__ == "__main__":
    run()
