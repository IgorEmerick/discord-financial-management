import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
  logger.info("Discord Expense Bot starting...")


if __name__ == "__main__":
  main()
