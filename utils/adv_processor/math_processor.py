from .basmath import AxisFilter, get_stable_yaw
from math import degrees, atan2, asin
from utils.registry import register_processor

@register_processor("Advanced")
class AdvProcessoring:
    def __init__(self, settings):
        self.filters = {
            axis: AxisFilter(axis.upper(),
                             settings.get(axis, {}).get("weight", 1.0),
                             settings.get(axis, {}).get("smooth", 0.3))
            for axis in ["yaw", "pitch", "roll"]
        }
        self.offsets = None
        self.pitch_static_offset = 12.0
        self.roll_sensitivity = 0.4
        print("[SYSTEM] AdvProcessoring (Original Logic Restored) initialized")

    def process(self, data):
        w, x, y, z = data.get("w", 1.0), data.get("x", 0.0), data.get("y", 0.0), data.get("z", 0.0)

        yaw = get_stable_yaw(w, x, y, z) * -1.0
        pitch = degrees(atan2(2.0 * (x * z - w * y), w*w - x*x - y*y + z*z)) * -1.0
        roll = degrees(asin(max(-1.0, min(1.0, 2.0 * (y * z + w * x))))) * -1.0

        if self.offsets is None:
            self.offsets = (yaw, pitch, roll)

        cal_yaw = (yaw - self.offsets[0] + 180.0) % 360.0 - 180.0
        cal_pitch = (pitch - self.offsets[1]) + self.pitch_static_offset
        cal_roll = (roll - self.offsets[2]) * self.roll_sensitivity

        cal_pitch = max(-55.0, min(55.0, cal_pitch))
        cal_roll = max(-30.0, min(30.0, cal_roll))

        return {
            "yaw": self.filters["yaw"].update(cal_yaw),
            "pitch": self.filters["pitch"].update(cal_pitch),
            "roll": self.filters["roll"].update(cal_roll)
        }