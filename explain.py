import os, re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ["NVIDIA_API_KEY"],
            timeout=25,
        )
    return _client


def template_explanation(v):
    steps = {
        "SENSOR_FAULT": "Inspect or recalibrate the flagged sensor before acting on its data.",
        "REAL_EVENT": "Treat as a genuine groundwater change and notify the water authority.",
        "UNCERTAIN": "Do a manual field check before trusting any of these readings.",
    }
    return f"{v['reason']} Next step: {steps.get(v['status'], 'Keep monitoring.')}"


def explain(v):
    if v["status"] in ("NORMAL", "WARMING_UP"):
        return v["reason"]
    prompt = (
        "You are a groundwater monitoring assistant. Based on this detector "
        f"output, explain in 2-3 simple sentences why this is a '{v['status']}', "
        "then give one recommended next step.\n"
        f"Verdict: {v['status']} (confidence {v['confidence']})\n"
        f"Faulty sensors: {v['faulty_sensors']}\n"
        f"Group-wide level change: {v['group_change']} m\n"
        f"Detector reasoning: {v['reason']}\n"
        "Do not invent numbers or facts beyond what is given. Be brief."
    )
    try:
        r = _get_client().chat.completions.create(
            model=os.environ["NVIDIA_MODEL_ID"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3,
        )
        text = (r.choices[0].message.content or "").strip()
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
        if text:
            return text
    except Exception as e:
        print("LLM failed, using template:", e)
    return template_explanation(v)