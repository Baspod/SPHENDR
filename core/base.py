from utils.registry import PROCESSOR_REGISTRY


class BaseSink:
    def __init__(self, math=None, **kwargs):
        self._registry = PROCESSOR_REGISTRY
        math_cfg = math or {}
        proc_name = math_cfg.get("active_processor", "Advanced")
        settings = math_cfg.get("settings", {})

        if proc_name not in self._registry:
            raise ValueError(
                f"[ERROR] Processor '{proc_name}' not found in registry! Available: {list(self._registry.keys())}")

        try:
            self.processor = self._registry[proc_name](settings)
        except Exception as e:
            raise RuntimeError(f"[ERROR] Failed to initialize processor '{proc_name}': {e}")

        self.on_init(**kwargs)

    def on_init(self, **kwargs):
        pass

    async def receive(self, data):
        if not hasattr(self, 'processor') or self.processor is None:
            print(f"[CRITICAL ERROR] {self.__class__.__name__} has no initialized processor!")
            return

        try:
            processed = self.processor.process(data)
            self.send_data(processed)
        except NotImplementedError:
            print(f"[CRITICAL ERROR] Method send_data is not implemented in plugin {self.__class__.__name__}!")
        except Exception as e:
            import traceback
            print(f"[CRITICAL ERROR] Processing error in {self.__class__.__name__}: {e}")
            traceback.print_exc()

    def send_data(self, data):
        raise NotImplementedError(f"Method send_data must be implemented in class {self.__class__.__name__}")