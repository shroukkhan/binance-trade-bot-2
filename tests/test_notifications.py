import os

import pytest
import yaml

from binance_trade_bot.notifications import NotificationHandler
from .common import infra  # type: ignore

APPRISE_CONFIG_PATH = "config/apprise.yml"


@pytest.fixture()
def generate_apprise_config(infra):
    data = {
        'version': 1,
        'urls': [
            'tgram://5092371024:AAGtfHjjxjW5X7OMtBx0TZXvBnJn3yX1HLw/1964979389'
        ]
    }
    with open(APPRISE_CONFIG_PATH, 'w') as f:
        yaml.dump(data, f)
        yield


@pytest.fixture(scope='function')
def notification_handler_enabled(generate_apprise_config):
    return NotificationHandler(enabled=True)


def test_notification_handler_initialization_disabled():
    notification_handler = NotificationHandler(False)
    assert not notification_handler.enabled
    
def test_notification_handler_initialization_enabled(notification_handler_enabled):
    assert notification_handler_enabled.enabled
    assert hasattr(notification_handler_enabled, "apobj")
    assert hasattr(notification_handler_enabled, "queue")


@pytest.mark.skipif(not os.path.exists(APPRISE_CONFIG_PATH), reason="Apprise config not found")
def test_send_notification(notification_handler_enabled):
    message = "Test message"
    attachments = ["attachment.png"]

    notification_handler_enabled.send_notification(message, attachments)
    queue_item = notification_handler_enabled.queue.get()

    assert queue_item == (message, attachments)
