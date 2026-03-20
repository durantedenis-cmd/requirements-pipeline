from pathlib import Path
import json
import hashlib

CURRENT_FILE = Path("canonical/requirements.json")
PREVIOUS_FILE = Path("canonical/requirements_previous.json")
OUTPUT_FILE = Path("canonical/deltas.json")


def make_hash(requirement: dict) -> str:
    payload = {
        "type": requirement.get("type"),
        "title": requirement.get("title"),
        "description": requirement.get("description"),
        "priority": requirement.get("priority"),
        "source_file": requirement.get("source_file"),
        "source_ref": requirement.get("source_ref"),
        "status": requirement.get("status"),
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def index_requirements(requirements):
    indexed = {}
    for req in requirements:
        key = req["requirement_id"]
        indexed[key] = {
            "requirement": req,
            "hash": make_hash(req)
        }
    return indexed


def main():
    if not CURRENT_FILE.exists():
        raise FileNotFoundError(f"Missing current requirements file: {CURRENT_FILE}")

    with CURRENT_FILE.open("r", encoding="utf-8") as f:
        current_data = json.load(f)

    current_requirements = current_data.get("requirements", [])
    current_index = index_requirements(current_requirements)

    if PREVIOUS_FILE.exists():
        with PREVIOUS_FILE.open("r", encoding="utf-8") as f:
            previous_data = json.load(f)
        previous_requirements = previous_data.get("requirements", [])
    else:
        previous_requirements = []

    previous_index = index_requirements(previous_requirements)

    new_items = []
    changed_items = []
    unchanged_items = []
    removed_items = []

    for req_id, current_entry in current_index.items():
        if req_id not in previous_index:
            new_items.append(current_entry["requirement"])
        else:
            if current_entry["hash"] != previous_index[req_id]["hash"]:
                changed_items.append(current_entry["requirement"])
            else:
                unchanged_items.append(current_entry["requirement"])

    for req_id, previous_entry in previous_index.items():
        if req_id not in current_index:
            removed_items.append(previous_entry["requirement"])

    output = {
        "summary": {
            "new": len(new_items),
            "changed": len(changed_items),
            "unchanged": len(unchanged_items),
            "removed": len(removed_items)
        },
        "new_requirements": new_items,
        "changed_requirements": changed_items,
        "unchanged_requirements": unchanged_items,
        "removed_requirements": removed_items
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    with PREVIOUS_FILE.open("w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=2, ensure_ascii=False)

    print(f"Created {OUTPUT_FILE}")
    print(f"Updated {PREVIOUS_FILE}")


if __name__ == "__main__":
    main()
