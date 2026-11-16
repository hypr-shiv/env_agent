import os
import re
import csv
import zlib
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("aquapulse.rag.loader")

def clean_text(text: str) -> str:
    """Removes irregular whitespace, non-printable characters, and normalizes line breaks."""
    if not text:
        return ""
    # Normalize unicode spaces and clean carriage returns
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse multiple whitespace characters into single space while preserving paragraph breaks
    paragraphs = text.split("\n\n")
    cleaned_paragraphs = []
    for p in paragraphs:
        cleaned_line = re.sub(r"[ \t]+", " ", p).strip()
        if cleaned_line:
            cleaned_paragraphs.append(cleaned_line)
    return "\n\n".join(cleaned_paragraphs)

def extract_txt_file(file_path: str) -> str:
    """Reads raw text or markdown file with utf-8 / fallback encoding."""
    encodings = ["utf-8", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Unable to decode text file {file_path} with supported encodings.")

def extract_csv_file(file_path: str) -> str:
    """
    Parses CSV file and converts each row into a structured natural language statement.
    Preserves column headers as contextual descriptors.
    """
    lines = []
    encodings = ["utf-8", "latin-1", "cp1252"]
    content = None
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or []
                for row_idx, row in enumerate(reader, 1):
                    row_parts = [f"{k.strip()}: {v.strip()}" for k, v in row.items() if k and v]
                    if row_parts:
                        lines.append(f"Record {row_idx} -> " + ", ".join(row_parts))
                break
        except UnicodeDecodeError:
            continue

    return "\n".join(lines)

def extract_pdf_file(file_path: str) -> str:
    """
    Extracts text from PDF files.
    Tries pypdf if installed; otherwise uses a lightweight pure-python stream extractor
    using built-in zlib decompression to extract text between BT ... ET.
    """
    # 1. Try pypdf if available
    try:
        import pypdf  # type: ignore
        reader = pypdf.PdfReader(file_path)
        extracted = []
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted.append(f"--- Page {page_idx + 1} ---\n{page_text}")
        if extracted:
            return "\n\n".join(extracted)
    except Exception:
        pass

    # 2. Pure Python Stream Extractor using zlib (zero external dependencies)
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()

    text_fragments = []
    # Find all FlateDecode streams
    stream_pattern = re.compile(rb"stream[\r\n]+(.*?)[\r\n]+endstream", re.DOTALL)
    for match in stream_pattern.finditer(pdf_bytes):
        stream_data = match.group(1)
        decompressed = b""
        try:
            decompressed = zlib.decompress(stream_data)
        except Exception:
            try:
                decompressed = zlib.decompress(stream_data, -zlib.MAX_WBITS)
            except Exception:
                continue

        # Look for PDF text show operations: (Text) Tj or [ (Text) ] TJ
        text_matches = re.findall(rb"\((.*?)\)\s*T[jJ]", decompressed)
        for tm in text_matches:
            try:
                decoded = tm.decode("latin-1", errors="ignore")
                # Remove escaped parentheses
                decoded = decoded.replace(r"\(", "(").replace(r"\)", ")")
                if len(decoded.strip()) > 1:
                    text_fragments.append(decoded)
            except Exception:
                pass

    if text_fragments:
        return " ".join(text_fragments)

    # 3. Fallback: extract any visible ASCII text strings
    ascii_strings = re.findall(rb"[\x20-\x7E]{4,}", pdf_bytes)
    return " ".join([s.decode("latin-1") for s in ascii_strings if not s.startswith(rb"/")])

def load_document(file_path: str) -> str:
    """Dispatches document extraction based on file extension."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Document not found at: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".txt", ".md", ".json", ".log"]:
        raw_text = extract_txt_file(file_path)
    elif ext == ".csv":
        raw_text = extract_csv_file(file_path)
    elif ext == ".pdf":
        raw_text = extract_pdf_file(file_path)
    else:
        # Default text attempt
        raw_text = extract_txt_file(file_path)

    return clean_text(raw_text)

def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Splits text into logical, overlapping chunks based on sentence boundaries
    or character count while maintaining readability.
    """
    if not text:
        return []

    # If text is smaller than chunk size, return as single chunk
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    # Split into paragraphs or sentences
    sentences = re.split(r"(?<=[.!?\n])\s+", text)
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if current_length + len(sentence) <= chunk_size:
            current_chunk.append(sentence)
            current_length += len(sentence) + 1
        else:
            if current_chunk:
                chunk_str = " ".join(current_chunk)
                chunks.append(chunk_str)
                # Keep overlap from end of current chunk
                overlap_chars = 0
                overlap_sentences = []
                for s in reversed(current_chunk):
                    if overlap_chars + len(s) <= chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_chars += len(s)
                    else:
                        break
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s) + 1 for s in current_chunk)
            else:
                # If a single sentence exceeds chunk_size, slice it
                for i in range(0, len(sentence), chunk_size - chunk_overlap):
                    chunks.append(sentence[i:i + chunk_size])
                current_chunk = []
                current_length = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

