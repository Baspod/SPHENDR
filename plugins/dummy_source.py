import asyncio
class DummySource:
    def __init__(self, **kwargs):
        pass
    async def start(self, bus):
        print("[SYSTEM] Running in DUMMY mode. No data source connected.")
        await asyncio.Event().wait()