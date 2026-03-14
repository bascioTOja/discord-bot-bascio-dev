import logging

from bot_app import BotApp
from config import load_config


logger = logging.getLogger(__name__)


def _setup_logging() -> None:
    logging.basicConfig(
        level="INFO",
        format="\033[94m%(asctime)s | %(levelname)-8s | %(name)s | %(message)s\033[0m",
    )

def main() -> None:
    config = load_config()

    bot = BotApp(config)

    bot.run(config.discord_token)


if __name__ == "__main__":
    _setup_logging()
    main()
