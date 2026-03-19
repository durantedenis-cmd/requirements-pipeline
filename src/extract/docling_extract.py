from pathlib import Path
import yaml
import json

CONFIG_FILE = Path("config/sources.yaml")
OUTPUT_FILE = Path("extracted/raw_extraction.json")

def main():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Missing config file: {CONFIG_FILE}")

    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    active_sources = [s for s in config.get("sources", []) if s.get("active")]

    result = {
        "active_sources_count": len(active_sources),
        "active_sources": active_sources
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Created {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
