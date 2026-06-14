from utils.registry import PROCESSOR_REGISTRY

class BaseSink:
    def __init__(self, math=None, **kwargs):
        self._registry = PROCESSOR_REGISTRY
        math_cfg = math or {}
        proc_name = math_cfg.get("active_processor", "Advanced")
        settings = math_cfg.get("settings", {})

        if proc_name not in self._registry:
            raise ValueError(f"[ERROR] Processor '{proc_name}' not found!")

        self.processor = self._registry[proc_name](settings)
        self.on_init(**kwargs)

    def on_init(self, **kwargs):
        pass

    async def receive(self, data):
        try:
            processed = self.processor.process(data)

            if processed is None:
                print(f"[DEBUG] [BaseSink] Процессор вернул None!")
                return

            self.send_data(processed)
        except Exception as e:
            print(f"[CRITICAL ERROR] Ошибка в BaseSink: {e}")

    def send_data(self, data):
        raise NotImplementedError("Метод send_data должен быть реализован в плагине")