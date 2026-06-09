import argparse
import json
import os
import re


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def extract_text_from_pdf(path: str) -> str:
    import fitz

    doc = fitz.open(path)
    pages = []
    for page in doc:
        pages.append(page.get_text("text"))
    return "\n".join(pages)


def extract_text_from_docx(path: str) -> str:
    try:
        import docx
    except ModuleNotFoundError as exc:
        raise RuntimeError("python-docx is required to extract .docx files. Install it with `pip install python-docx`.") from exc

    doc = docx.Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def build_task(entry_id: str, text: str, source_path: str) -> dict:
    return {
        "id": entry_id,
        "data": {
            "text": text,
            "source": source_path,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract raw2 resume text into Label Studio JSON tasks.")
    parser.add_argument("--input-dir", default="raw2", help="Input directory containing raw PDF/DOCX resumes.")
    parser.add_argument("--output", default="raw2_labelstudio.json", help="Output JSON file for Label Studio tasks.")
    parser.add_argument("--skip-docx", action="store_true", help="Skip .docx files if python-docx is unavailable.")
    parser.add_argument("--verbose", action="store_true", help="Print processing details.")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        raise FileNotFoundError(f"Input directory not found: {args.input_dir}")

    tasks = []
    processed = 0
    skipped = 0
    errors = []

    for filename in sorted(os.listdir(args.input_dir)):
        path = os.path.join(args.input_dir, filename)
        if not os.path.isfile(path):
            continue

        ext = os.path.splitext(filename)[1].lower()
        try:
            if ext == ".pdf":
                text = extract_text_from_pdf(path)
            elif ext == ".docx":
                if args.skip_docx:
                    skipped += 1
                    continue
                text = extract_text_from_docx(path)
            else:
                skipped += 1
                continue
        except Exception as exc:
            errors.append({"file": filename, "error": str(exc)})
            if args.verbose:
                print(f"[ERROR] {filename}: {exc}")
            skipped += 1
            continue

        text = normalize_text(text)
        if not text:
            if args.verbose:
                print(f"[WARN] {filename}: extracted text is empty")
            skipped += 1
            continue

        entry_id = os.path.splitext(filename)[0]
        tasks.append(build_task(entry_id, text, filename))
        processed += 1
        if args.verbose:
            print(f"[OK] {filename}: {len(text)} chars")

    output_data = tasks
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Processed {processed} files, skipped {skipped} files.")
    print(f"Saved {len(tasks)} tasks to {args.output}")
    if errors:
        print("Errors:")
        for err in errors:
            print(f"  - {err['file']}: {err['error']}")


if __name__ == "__main__":
    main()
