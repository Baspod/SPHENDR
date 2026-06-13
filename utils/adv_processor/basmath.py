from math import degrees, atan2, asin

def get_stable_yaw(w, x, y, z):

    qW, qX, qY, qZ = w, y, x, z
    test = qX * qZ + qY * qW
    if test > 0.499999: return degrees(2.0 * atan2(qX, qW))
    elif test < -0.499999: return degrees(-2.0 * atan2(qX, qW))
    else: return degrees(atan2(2.0 * qZ * qW - 2.0 * qX * qY, 1.0 - 2.0 * (qY * qY + qZ * qZ)))

class AxisFilter:
    def __init__(self, name, weight, smooth):
        self.name, self.weight, self.smooth = name, weight, smooth
        self.value, self.initialized = 0.0, False

    def update(self, new_val):
        if self.weight <= 0: return 0.0
        weighted_val = new_val * self.weight
        if not self.initialized:
            self.value, self.initialized = weighted_val, True
            return self.value


        if abs(weighted_val - self.value) > 45.0:
            self.value = weighted_val
            return self.value

        self.value = (self.smooth * weighted_val) + ((1.0 - self.smooth) * self.value)
        return self.value