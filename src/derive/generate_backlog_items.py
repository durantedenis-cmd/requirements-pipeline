from pathlib import Path
import json
import os
from openai import OpenAI

INPUT_FILE = Path("canonical/requirements.json")
OUTPUT_DIR = Path("derived")


def load_requirements():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

    with INPUT_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("requirements", [])


def call_openai(requirements):
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")

    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")
    if not model:
        raise RuntimeError("Missing OPENAI_MODEL environment variable.")

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a senior business analyst.

Convert the following canonical requirements into a structured agile backlog.

Return ONLY valid JSON with this exact structure:
{{
  "epics": [
    {{
      "epic_id": "EP-001",
      "title": "...",
      "description": "...",
      "linked_requirement_ids": ["..."]
    }}
  ],
  "features": [
    {{
      "feature_id": "FEAT-001",
      "epic_id": "EP-001",
      "title": "...",
      "description": "...",
      "linked_requirement_ids": ["..."]
    }}
  ],
  "stories": [
    {{
      "story_id": "US-001",
      "feature_id": "FEAT-001",
      "title": "...",
      "description": "...",
      "as_a": "...",
      "i_want": "...",
      "so_that": "...",
      "acceptance_criteria": ["..."],
      "linked_requirement_ids": ["..."]
    }}
  ],
  "use_cases": [
    {{
      "use_case_id": "UC-001",
      "story_id": "US-001",
      "title": "...",
      "actor": "...",
      "preconditions": ["..."],
      "main_flow": ["..."],
      "postconditions": ["..."],
      "linked_requirement_ids": ["..."]
    }}
  ]
}}

Canonical requirements:
{json.dumps(requirements, indent=2, ensure_ascii=False)}
""".strip()

    response = client.responses.create(
        model=model,
        input=prompt
    )

    raw = response.output_text.strip()
    return json.loads(raw)


def save_outputs(result):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    outputs = {
        "epics.json": result.get("epics", []),
        "features.json": result.get("features", []),
        "stories.json": result.get("stories", []),
        "use_cases.json": result.get("use_cases", []),
    }

    for filename, payload in outputs.items():
        output_path = OUTPUT_DIR / filename
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    print("Created derived/epics.json")
    print("Created derived/features.json")
    print("Created derived/stories.json")
    print("Created derived/use_cases.json")


def main():
    requirements = load_requirements()
    result = call_openai(requirements)
    save_outputs(result)


if __name__ == "__main__":
    main()
