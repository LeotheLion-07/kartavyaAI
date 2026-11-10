import os
import json
import csv
import io
from typing import Dict, Any, List
import pypdf

def parse_file_content(file_path: str, filename: str, content_bytes: bytes) -> Dict[str, Any]:
    """Parses various file types into text and chunks."""
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    metadata = {"filename": filename, "extension": ext, "size_bytes": len(content_bytes)}
    
    try:
        if ext == ".pdf":
            reader = pypdf.PdfReader(io.BytesIO(content_bytes))
            metadata["num_pages"] = len(reader.pages)
            pages_text = []
            for i, page in enumerate(reader.pages):
                p_text = page.extract_text() or ""
                pages_text.append(f"--- Page {i+1} ---\n" + p_text)
            text = "\n\n".join(pages_text)
        elif ext in [".md", ".txt"]:
            text = content_bytes.decode("utf-8", errors="replace")
        elif ext == ".csv":
            decoded = content_bytes.decode("utf-8", errors="replace")
            reader = csv.reader(io.StringIO(decoded))
            rows = list(reader)
            metadata["row_count"] = len(rows)
            text = "\n".join([", ".join(row) for row in rows])
        elif ext == ".json":
            decoded = content_bytes.decode("utf-8", errors="replace")
            data = json.loads(decoded)
            metadata["json_keys"] = list(data.keys()) if isinstance(data, dict) else len(data)
            text = json.dumps(data, indent=2)
        else:
            text = content_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        text = f"Error extracting content: {str(e)}"
        metadata["error"] = str(e)
        
    return {
        "text": text,
        "metadata": metadata
    }

def chunk_text(text: str, chunk_size_lines: int = 15) -> List[Dict[str, Any]]:
    """Splits text into line-numbered chunks."""
    lines = text.split("\n")
    chunks = []
    
    for i in range(0, len(lines), chunk_size_lines):
        chunk_lines = lines[i:i + chunk_size_lines]
        chunk_text = "\n".join(chunk_lines)
        if chunk_text.strip():
            chunks.append({
                "chunk_index": len(chunks),
                "line_start": i + 1,
                "line_end": min(i + chunk_size_lines, len(lines)),
                "text": chunk_text
            })
    return chunks
