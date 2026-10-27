import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from simulator import Simulator
from detector import Detector
from explain import explain

TICK = 0.5
state = {}


def reset():
    sim = Simulator()
    state.update(sim=sim, det=Detector(sim.names), history=[],
                 alerts=[], latest=None, last_status=None)


async def fill(alert, verdict):
    alert["explanation"] = await asyncio.to_thread(explain, verdict)


async def loop():
    while True:
        sim, det = state["sim"], state["det"]
        reading = sim.step()
        verdict = det.update(reading)
        state["history"].append(reading)
        state["history"] = state["history"][-120:]
        state["latest"] = verdict
        if verdict["status"] != state["last_status"]:
            state["last_status"] = verdict["status"]
            if verdict["status"] in ("SENSOR_FAULT", "REAL_EVENT", "UNCERTAIN"):
                alert = {"t": verdict["t"], "status": verdict["status"],
                         "confidence": verdict["confidence"],
                         "faulty": list(verdict["faulty_sensors"]),
                         "explanation": "AI is analyzing..."}
                state["alerts"].insert(0, alert)
                asyncio.create_task(fill(alert, verdict))
        await asyncio.sleep(TICK)


@asynccontextmanager
async def lifespan(app):
    reset()
    task = asyncio.create_task(loop())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def home():
    return FileResponse("index.html")


@app.get("/api/state")
def get_state():
    return {"names": state["sim"].names, "history": state["history"],
            "verdict": state["latest"], "alerts": state["alerts"][:8]}


@app.post("/api/scenario/{name}")
def scenario(name: str, sensor: str = "S3"):
    sim = state["sim"]
    if name in ("drop", "spike", "flatline", "drift", "dropout"):
        sim.inject_fault(sensor, name)
    elif name == "real":
        sim.trigger_real_event()
    elif name == "recover":
        sim.clear_real_event()
    elif name == "all_flatline":
        for n in sim.names:
            sim.inject_fault(n, "flatline")
    elif name == "reset":
        reset()
    else:
        raise HTTPException(404, "unknown scenario")
    return {"ok": True}