from __future__ import annotations

import asyncio

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


async def run_worker() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("worker.started", environment=settings.env)
    while True:
        logger.info("worker.heartbeat")
        await asyncio.sleep(60)


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
