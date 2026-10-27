import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ["NVIDIA_API_KEY"],
)
r = client.chat.completions.create(
    model=os.environ["NVIDIA_MODEL_ID"],
    messages=[{"role": "user", "content": "Say hello"}],
)
print(r.choices[0].message.content)