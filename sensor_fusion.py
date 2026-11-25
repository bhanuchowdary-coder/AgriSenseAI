
import math


class KalmanFilter:
    def __init__(self, process_noise=0.1,
                 measurement_noise=2.0):
        self.Q = process_noise
        self.R = measurement_noise
        self.P = 1.0
        self.x = None

    def update(self, measurement):
        if self.x is None:
            self.x = measurement
            return self.x

        # Prediction
        self.P += self.Q

        # Kalman gain
        K = self.P / (self.P + self.R)

        # State estimation
        self.x += K * (measurement - self.x)

        # Update uncertainty
        self.P = (1 - K) * self.P

        return round(self.x, 3)


def filter_sensor_data(readings):
    if not isinstance(readings, list) or not readings:
        raise ValueError("A non-empty readings list is required")

    kalman = KalmanFilter()
    filtered = []

    for reading in readings:
        value = float(reading)

        if not math.isfinite(value):
            raise ValueError("Readings must be finite numbers")

        filtered.append(kalman.update(value))

    return filtered
