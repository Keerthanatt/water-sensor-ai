import math
import random

DURATIONS = {"spike": 3, "flatline": 20, "drift": 40, "drop": 40, "dropout": 10}

class Simulator:
    def __init__(self, n_sensors=5, seed=None):
        if seed is not None:
            random.seed(seed)
        self.t = 0
        self.names = [f"S{i+1}" for i in range(n_sensors)]
        self.base = {n: 10 + random.uniform(-1.5, 1.5) for n in self.names}
        self.last = dict(self.base)
        self.faults = {}
        self.drawdown = 0.0
        self.drawdown_target = 0.0

    def inject_fault(self, sensor, kind):
        """kind: spike, flatline, drift, drop, dropout"""
        self.faults[sensor] = {"type": kind, "age": 0,
                               "duration": DURATIONS[kind]}

    def trigger_real_event(self, depth=3.0):
        """Regional drawdown: ALL sensors fall together."""
        self.drawdown_target = depth

    def clear_real_event(self):
        self.drawdown_target = 0.0

    def step(self):
        self.t += 1
        if self.drawdown < self.drawdown_target:
            self.drawdown = min(self.drawdown + 0.15, self.drawdown_target)
        elif self.drawdown > self.drawdown_target:
            self.drawdown = max(self.drawdown - 0.1, self.drawdown_target)

        readings = {}
        for n in self.names:
            seasonal = 0.8 * math.sin(2 * math.pi * self.t / 200)
            value = self.base[n] + seasonal - self.drawdown
            value += random.gauss(0, 0.05)

            f = self.faults.get(n)
            if f:
                f["age"] += 1
                k = f["type"]
                if k == "spike":
                    value += 8
                elif k == "flatline":
                    value = f.setdefault("frozen", self.last[n])
                elif k == "drift":
                    value += 0.1 * f["age"]
                elif k == "drop":
                    value -= 4
                elif k == "dropout":
                    value = None
                if f["age"] >= f["duration"]:
                    del self.faults[n]

            if value is not None:
                self.last[n] = value
                value = round(value, 3)
            readings[n] = value
        return {"t": self.t, "readings": readings}


if __name__ == "__main__":
    sim = Simulator(seed=1)
    for i in range(60):
        if i == 20:
            sim.inject_fault("S3", "drop")      # isolated fault
        if i == 45:
            sim.trigger_real_event()            # real regional drop
        print(sim.step())