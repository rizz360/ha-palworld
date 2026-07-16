"""Constants for the Palworld Server integration."""
from datetime import timedelta
import logging

DOMAIN = "palworld"
LOGGER = logging.getLogger(__package__)

DEFAULT_PORT = 8212
DEFAULT_USERNAME = "admin"
DEFAULT_NAME = "Palworld Server"
DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 10

CONF_SCAN_INTERVAL = "scan_interval"

UPDATE_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

MANUFACTURER = "Pocketpair"
MODEL = "Palworld Dedicated Server"

# Service names
SERVICE_ANNOUNCE = "announce"
SERVICE_KICK = "kick"
SERVICE_BAN = "ban"
SERVICE_UNBAN = "unban"
SERVICE_SAVE = "save_world"
SERVICE_SHUTDOWN = "shutdown"
SERVICE_STOP = "force_stop"

ATTR_MESSAGE = "message"
ATTR_USERID = "userid"
ATTR_WAITTIME = "waittime"
