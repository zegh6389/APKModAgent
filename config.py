import os


# Basic configurable values for the injected updater logic.
# These defaults keep current behaviour but can be overridden with environment
# variables in your deployment (e.g. DigitalOcean App Platform).


UPDATE_URL = os.getenv(
    "UPDATE_URL",
    "https://your-website.com/update_config.json",
)

TELEGRAM_URL = os.getenv(
    "TELEGRAM_URL",
    "https://t.me/YourTelegramChannel",
)

WELCOME_TITLE = os.getenv(
    "WELCOME_TITLE",
    "Welcome!",
)

WELCOME_MESSAGE = os.getenv(
    "WELCOME_MESSAGE",
    "Thanks for using our Mod. Join us on Telegram for updates!",
)

UPDATE_DIALOG_TITLE = os.getenv(
    "UPDATE_DIALOG_TITLE",
    "Update Available",
)

UPDATE_DIALOG_MESSAGE = os.getenv(
    "UPDATE_DIALOG_MESSAGE",
    "A new version is available. check our telegram channel",
)