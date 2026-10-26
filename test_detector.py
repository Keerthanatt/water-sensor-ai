from simulator import Simulator
from detector import Detector


def run(title, setup, steps=90):
    sim = Simulator(seed=1)
    det = Detector(sim.names)
    print("\n===", title)
    last = None
    for i in range(steps):
        setup(sim, i)
        r = det.update(sim.step())
        if r["status"] != last:
            print(r["t"], r["status"], r["confidence"], "-", r["reason"])
            last = r["status"]


def one_fault(sim, i):
    if i == 30:
        sim.inject_fault("S3", "drop")

def real_event(sim, i):
    if i == 30:
        sim.trigger_real_event()

def all_fail(sim, i):
    if i == 30:
        for n in sim.names:
            sim.inject_fault(n, "flatline")

run("ONE SENSOR DROPS (fault)", one_fault)
run("ALL SENSORS DROP (real)", real_event)
run("ALL SENSORS FLATLINE (uncertain)", all_fail)