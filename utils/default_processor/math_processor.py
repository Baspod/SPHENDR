from utils.registry import register_processor

@register_processor("Default")
class DefaultProcessor:

    def __init__(self, settings):

        self.settings = settings
        print("[DEBUG] Default initialized")
    def process(self, data):

        processed = data.copy()
        for axis in ["yaw", "pitch", "roll"]:

            cfg = self.settings.get(axis, {"multiplier": 1.0})
            val = processed.get(axis, 0.0)
            processed[axis] = val * cfg.get("multiplier", 1.0)
        return processed