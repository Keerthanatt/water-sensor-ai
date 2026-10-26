import statistics
from collections import deque

WARMUP = 20    # steps used to learn each sensor's baseline
JUMP = 3.0     # sudden jump between readings
DEV = 1.5      # deviation from neighbors
REAL = 1.5     # group-wide change that counts as real
FLAT_N = 5     # identical readings in a row = flatline


class Detector:
    def __init__(self, names):
        self.names = names
        self.hist = {n: deque(maxlen=30) for n in names}
        self.warm = {n: [] for n in names}
        self.base = {}

    def update(self, reading):
        t, vals = reading["t"], reading["readings"]
        N = len(self.names)
        for n in self.names:
            self.hist[n].append(vals[n])
            if t <= WARMUP and vals[n] is not None:
                self.warm[n].append(vals[n])

        if t <= WARMUP:
            if t == WARMUP:
                self.base = {n: sum(self.warm[n]) / len(self.warm[n])
                             for n in self.names}
            return {"t": t, "status": "WARMING_UP", "confidence": 0,
                    "faulty_sensors": {}, "group_change": 0,
                    "reason": "Learning normal behavior."}

        changes = {n: vals[n] - self.base[n]
                   for n in self.names if vals[n] is not None}
        group = statistics.median(changes.values()) if changes else 0

        flags = {n: [] for n in self.names}
        for n in self.names:
            v = vals[n]
            h = list(self.hist[n])
            if v is None:
                flags[n].append("dropout (no data)")
                continue
            prev = [x for x in h[:-1] if x is not None]
            if prev and abs(v - prev[-1]) > JUMP:
                flags[n].append("sudden spike/jump")
            last = h[-FLAT_N:]
            if (len(last) == FLAT_N and None not in last
                    and max(last) - min(last) == 0):
                flags[n].append("flatline (stuck value)")
            dev = changes[n] - group
            if abs(dev) > DEV and not flags[n]:
                recent = [x for x in h[-10:] if x is not None]
                jumps = [abs(a - b) for a, b in zip(recent[1:], recent)]
                kind = ("sudden shift" if jumps and max(jumps) > JUMP
                        else "gradual drift")
                flags[n].append(f"{kind} vs neighbors")

        faulty = {n: f for n, f in flags.items() if f}
        moving = [n for n in changes if abs(changes[n]) > REAL]
        real = abs(group) > REAL and len(moving) >= 0.6 * N

        if len(faulty) >= 0.6 * N:
            status, conf = "UNCERTAIN", 0.3
            reason = (f"{len(faulty)} of {N} sensors show problems at once. "
                      "This looks like a common-cause failure. "
                      "Manual verification needed.")
        elif real:
            status = "REAL_EVENT"
            conf = round(min(0.95, len(moving) / N), 2)
            direction = "dropped" if group < 0 else "risen"
            reason = (f"{len(moving)} of {N} sensors agree: groundwater has "
                      f"{direction} by about {abs(group):.1f} m.")
            if faulty:
                reason += f" Separately, {', '.join(faulty)} look faulty."
        elif faulty:
            status = "SENSOR_FAULT"
            healthy = N - len(faulty)
            conf = round(min(0.95, 0.5 + 0.1 * healthy), 2)
            parts = [f"{n}: {', '.join(f)}" for n, f in faulty.items()]
            reason = ("; ".join(parts) + f". The other {healthy} nearby "
                      "sensors are stable, so this is likely a sensor "
                      "fault, not a groundwater change.")
        else:
            status, conf, reason = "NORMAL", 0.9, "All sensors consistent."

        return {"t": t, "status": status, "confidence": conf,
                "faulty_sensors": faulty, "group_change": round(group, 2),
                "reason": reason}