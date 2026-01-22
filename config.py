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

# Behaviour flags controlling how aggressively we strip third‑party mods and
# whether we inject our own updater logic. All are environment driven so you
# can tweak behaviour per deployment without changing code.

STRIP_GETMODPC = os.getenv("STRIP_GETMODPC", "1") == "1"

ENABLE_UPDATER = os.getenv("ENABLE_UPDATER", "1") == "1"