import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("DataBus")

class DataBus:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    async def publish(self, data):
        if not self.subscribers:
            return

        for sub in self.subscribers:
            asyncio.create_task(self._safe_receive(sub, data))

    async def _safe_receive(self, sub, data):
        try:
            await sub.receive(data)
        except Exception as e:
            name = getattr(sub, 'name', 'UnknownPlugin')
            logger.error(f"Plugin '{name}' crashed: {e}")