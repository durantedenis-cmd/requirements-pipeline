from pathlib import Path
import json
import os
from openai import OpenAI

REQ_FILE = Path("canonical/requirements.json")
USE_CASES_FILE = Path("derived/use_cases.json")
OUTPUT_DIR = Path("derived")


def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def call_openai(requirements, use_cases):
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5")

    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")
    
    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a senior QA analyst.

Using the canonical requirements and use cases below, generate:
- test scenarios
- manual test cases
- automation candidates for Playwright/Python

Return ONLY valid JSON with this exact structure:
{{
  "test_scenarios": [
    {{
      "test_scenario_id": "TS-001",
      "title": "...",
      "description": "...",
      "linked_requirement_ids": ["..."],
      "linked_use_case_ids": ["..."]
    }}
  ],
  "manual_test_cases": [
    {{
      "test_case_id": "TC-001",
      "test_scenario_id": "TS-001",
      "title": "...",
      "preconditions": ["..."],
      "steps": [
        {{
          "step_no": 1,
          "action": "...",
          "expected_result": "..."
        }}
      ],
      "linked_requirement_ids": ["..."]
    }}
  ],
  "automation_candidates": [
    {{
      "automation_id": "AT-001",
      "test_scenario_id": "TS-001",
      "title": "...",
      "priority": "high",
      "recommended_framework": "playwright-python",
      "test_type": "ui",
      "linked_requirement_ids": ["..."]
    }}
  ]
}}

Canonical requirements:
{json.dumps(requirements, indent=2, ensure_ascii=False)}

Use cases:
{json.dumps(use_cases, indent=2, ensure_ascii=False)}
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
        "test_scenarios.json": result.get("test_scenarios", []),
        "manual_test_cases.json": result.get("manual_test_cases", []),
        "automation_candidates.json": result.get("automation_candidates", []),
    }

    for filename, payload in outputs.items():
        output_path = OUTPUT_DIR / filename
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    print("Created derived/test_scenarios.json")
    print("Created derived/manual_test_cases.json")
    print("Created derived/automation_candidates.json")


def main():
    req_data = load_json(REQ_FILE, {})
    requirements = req_data.get("requirements", []) if isinstance(req_data, dict) else req_data
    use_cases = load_json(USE_CASES_FILE, [])

    result = call_openai(requirements, use_cases)
    save_outputs(result)


if __name__ == "__main__":
    main()
