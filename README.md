# Groundwater Sensor Fault Detection AI

An AI agent that decides whether a change in groundwater readings is a
**real event** or a **sensor fault**, and explains its verdict in plain
language using an NVIDIA Nemotron model.

Built for the **Nebius x NVIDIA Global AI Hackathon** (problem statement PS-07).

| | |
|---|---|
| **Team** | Synaptix |
| **Members** | Akshathaa P K, Keerthana T, Harini P |
| **College** | PSG Institute of Technology and Applied Research |
| **Repository** | https://github.com/Keerthanatt/water-sensor-ai |
| **Demo video** | Coming soon |

## The problem
Groundwater monitoring depends on remote sensors. A sudden drop in a
reading could be a real drawdown (drought, heavy pumping) or a broken
sensor. Treating a fault as an event, or an event as a fault, leads to
wrong decisions.

## How it works
1. **Simulator** (`simulator.py`) generates readings from 5 sensors and
   injects faults (spike, flatline, drift, drop, dropout) as well as real
   drawdown events.
2. **Detector** (`detector.py`) uses statistical rules: per-sensor checks
   and neighbor comparison. It returns one of four verdicts:
   `SENSOR_FAULT`, `REAL_EVENT`, `UNCERTAIN` or `NORMAL`, with a
   confidence score.
3. **Explainer** (`explain.py`) sends the verdict to an NVIDIA Nemotron
   model, which explains the reasoning. If the API fails, a template
   fallback produces the explanation.
4. **Backend** (`main.py`) is a FastAPI app with a background loop and
   scenario endpoints.
5. **Dashboard** (`index.html`) shows a live Chart.js graph, a status
   banner, an alerts panel and scenario buttons.

The verdict comes from transparent statistical rules. The LLM only
explains it; it does not decide it.

## Tech stack
Python, FastAPI, Chart.js, NVIDIA Nemotron (via `integrate.api.nvidia.com`)

## Setup
```
pip install fastapi uvicorn openai python-dotenv
```
Create a `.env` file (never commit it):
```
NVIDIA_API_KEY=your_key_here
NVIDIA_MODEL_ID=nvidia/nemotron-3.5-super-vl-120b-a12b
```
Run:
```
uvicorn main:app
```
Open http://127.0.0.1:8000

## Demo scenarios
- **Sensor fault:** S3 drops while its neighbors stay steady.
- **Real event:** a drought lowers all sensors together.
- **Uncertain:** all sensors flatline, so the system asks for a manual check.

## Limitations
- Simulated data only.
- If all sensors fail the same believable way, the system reports
  UNCERTAIN and asks for a manual check.
- Thresholds are tuned for simulated data.

## Related work
Groundwater and water-sensor quality control is an established field.
This project does not claim to be the first; it focuses on **explainable
fault-vs-event classification**, meaning a plain-language reason for each
verdict.

- **USGS groundwater quality-assurance plans** set out manual QA/QC
  procedures for collecting, processing and publishing groundwater data,
  for example the Kansas plan:
  https://pubs.usgs.gov/publication/ofr20141060
- **Royal Eijkelkamp (ROAK platform)** offers commercial groundwater
  telemetry with dashboards, alerts and data validation:
  https://www.royaleijkelkamp.com/solutions/for-applications/data/telemetry/
  Their research experiment on automatic validation, which applies AI to
  help maintenance staff, is at https://portal.effra.eu/result/show/6870
- **iFLUX** combines a groundwater sensor with a cloud platform that uses
  machine learning for anomaly detection:
  https://cordis.europa.eu/project/id/190191933/reporting/es
- **PyHydroQC** (Utah State University) is an open-source Python package
  for automated anomaly detection and correction in aquatic sensor data:
  https://par.nsf.gov/servlets/purl/10373342
- **Reichmann et al. (AGU)** use neighboring sensors to predict readings
  for QC in a coastal water-level network, and note the risk of discarding
  real extreme events as errors, the same fault-vs-event problem we address:
  https://agu.confex.com/agu/osm20/preliminaryview.cgi/Paper657786.html

## License
See [LICENSE](LICENSE).