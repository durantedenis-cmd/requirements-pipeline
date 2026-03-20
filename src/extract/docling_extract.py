from pathlib import Path
import json
import yaml

from docling.document_converter import DocumentConverter

CONFIG_FILE = Path("config/sources.yaml")
OUTPUT_FILE = Path("extracted/raw_extraction.json")


def main():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Missing config file: {CONFIG_FILE}")

    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    active_sources = [s for s in config.get("sources", []) if s.get("active")]

    converter = DocumentConverter()
    documents = []

    for source in active_sources:
        file_path = Path(source["file"])

        if not file_path.exists():
            documents.append(
                {
                    "file": source["file"],
                    "type": source.get("type"),
                    "active": source.get("active", False),
                    "status": "error",
                    "error": f"File not found: {file_path}",
                }
            )
            continue

        try:
            result = converter.convert(str(file_path))
            doc = result.document
            markdown = doc.export_to_markdown()

            documents.append(
                {
                    "file": source["file"],
                    "type": source.get("type"),
                    "active": source.get("active", False),
                    "status": "success",
                    "format": file_path.suffix.lower(),
                    "markdown": markdown,
                }
            )
        except Exception as e:
            documents.append(
                {
                    "file": source["file"],
                    "type": source.get("type"),
                    "active": source.get("active", False),
                    "status": "error",
                    "format": file_path.suffix.lower(),
                    "error": str(e),
                }
            )

    output = {
        "documents_count": len(documents),
        "documents": documents,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Created {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
