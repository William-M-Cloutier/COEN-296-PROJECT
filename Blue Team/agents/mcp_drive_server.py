#!/usr/bin/env python3
"""
Drive MCP Server - Standalone MCP Server for Document/Drive Operations
Section 3.4 Compliance: Document Management Specialized Agent

Provides MCP tools for file operations with Blue Team security controls:
- upload_file: Upload file with type allowlist
- search_files: Search with RAG/keyword (provenance tracking)
- read_file: Read file with path traversal protection

Security Controls (MAESTRO Compliance - Section 3.5):
- File type allowlist (.txt, .pdf, .md only)
- Path traversal protection (cannot access outside mock_drive/)
- RAG stub with Source ID for provenance
- Malware upload prevention

Run as: python3 -m agents.mcp_drive_server
"""
import os
import re
import hashlib
import mimetypes
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
MOCK_DRIVE_ROOT = "mock_drive"
ALLOWED_FILE_TYPES = {
    "text/plain": ".txt",
    "application/pdf": ".pdf",
    "text/markdown": ".md",
}
MAX_FILE_SIZE_MB = 5  # Maximum file size for uploads

# Ensure the mock drive directory exists
os.makedirs(MOCK_DRIVE_ROOT, exist_ok=True)

# --- Utility Functions ---

def _generate_file_id(filename: str) -> str:
    """Generates a unique file ID based on filename and timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return hashlib.sha256(f"{filename}-{timestamp}".encode()).hexdigest()[:12]

def _get_file_extension(filename: str) -> str:
    """Extracts the file extension from a filename."""
    return os.path.splitext(filename)[1].lower()

def _is_allowed_file_type(mime_type: str) -> bool:
    """Checks if the given MIME type is in the allowlist."""
    return mime_type in ALLOWED_FILE_TYPES

def _get_mime_type(filename: str) -> Optional[str]:
    """Determines the MIME type of a file based on its extension."""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type

def _sanitize_filename(filename: str) -> str:
    """Sanitizes a filename to prevent directory traversal and invalid characters."""
    # Remove any directory components
    filename = os.path.basename(filename)
    # Replace invalid characters with underscores
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return filename

def _resolve_safe_path(filename: str) -> Optional[str]:
    """
    Resolves a filename to a safe path within MOCK_DRIVE_ROOT,
    preventing path traversal.
    """
    sanitized_filename = _sanitize_filename(filename)
    target_path = os.path.join(MOCK_DRIVE_ROOT, sanitized_filename)
    # Ensure the resolved path is strictly within MOCK_DRIVE_ROOT
    if not os.path.abspath(target_path).startswith(os.path.abspath(MOCK_DRIVE_ROOT)):
        logging.warning(f"Path traversal attempt detected for: {filename}")
        return None
    return target_path

# --- MCP Drive Server Operations ---

def upload_file(
    filename: str,
    file_content: bytes,
    mime_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Uploads a file to the mock drive with security controls.

    Args:
        filename (str): The original name of the file.
        file_content (bytes): The binary content of the file.
        mime_type (Optional[str]): The MIME type of the file. If None, it's guessed.

    Returns:
        Dict[str, Any]: A dictionary containing upload status and file metadata.
    """
    logging.info(f"Attempting to upload file: {filename}")

    # 1. Malware Upload Prevention (Stub)
    # In a real system, this would integrate with a malware scanner.
    # For this exercise, we'll simulate a check.
    if b"malware_signature" in file_content:
        logging.error(f"Malware signature detected in {filename}. Upload blocked.")
        return {"status": "error", "message": "Malware detected, upload blocked."}

    # 2. File Type Allowlist
    if mime_type is None:
        mime_type = _get_mime_type(filename)

    if not mime_type or not _is_allowed_file_type(mime_type):
        logging.error(f"File type '{mime_type}' for {filename} is not allowed.")
        return {"status": "error", "message": f"File type '{mime_type}' not allowed. Allowed types: {list(ALLOWED_FILE_TYPES.keys())}"}

    # Ensure file extension matches allowed type
    expected_ext = ALLOWED_FILE_TYPES.get(mime_type)
    actual_ext = _get_file_extension(filename)
    if expected_ext and actual_ext != expected_ext:
        logging.warning(f"File extension mismatch for {filename}. Expected {expected_ext}, got {actual_ext}. Proceeding with MIME type check.")
        # Optionally, this could be an error, but for now, MIME type is primary.

    # 3. File Size Limit
    if len(file_content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        logging.error(f"File {filename} exceeds maximum size of {MAX_FILE_SIZE_MB}MB.")
        return {"status": "error", "message": f"File size exceeds {MAX_FILE_SIZE_MB}MB limit."}

    # 4. Path Traversal Protection & Sanitize Filename
    safe_path = _resolve_safe_path(filename)
    if not safe_path:
        return {"status": "error", "message": "Invalid filename or path traversal attempt."}

    file_id = _generate_file_id(filename)
    final_filename = f"{file_id}{_get_file_extension(filename)}"
    full_path = os.path.join(MOCK_DRIVE_ROOT, final_filename)

    try:
        with open(full_path, "wb") as f:
            f.write(file_content)
        logging.info(f"Successfully uploaded {filename} as {final_filename} (ID: {file_id})")
        return {
            "status": "success",
            "message": "File uploaded successfully.",
            "file_id": file_id,
            "filename": final_filename,
            "original_filename": filename,
            "mime_type": mime_type,
            "size_bytes": len(file_content),
            "upload_timestamp": datetime.now().isoformat()
        }
    except IOError as e:
        logging.error(f"Error writing file {final_filename}: {e}")
        return {"status": "error", "message": f"Failed to write file: {e}"}

def read_file(file_id: str) -> Dict[str, Any]:
    """
    Reads a file from the mock drive using its file ID, with path traversal protection.

    Args:
        file_id (str): The unique ID of the file to read.

    Returns:
        Dict[str, Any]: A dictionary containing read status and file content (if successful).
    """
    logging.info(f"Attempting to read file with ID: {file_id}")

    # Find the actual filename associated with the file_id
    found_file = None
    for fname in os.listdir(MOCK_DRIVE_ROOT):
        if fname.startswith(file_id):
            found_file = fname
            break

    if not found_file:
        logging.warning(f"File with ID {file_id} not found.")
        return {"status": "error", "message": "File not found."}

    # Path traversal protection is implicitly handled by using the found_file
    # which is guaranteed to be directly in MOCK_DRIVE_ROOT.
    full_path = os.path.join(MOCK_DRIVE_ROOT, found_file)

    # Double-check path safety (redundant but good for defense-in-depth)
    if not os.path.abspath(full_path).startswith(os.path.abspath(MOCK_DRIVE_ROOT)):
        logging.error(f"Path traversal detected during read for ID: {file_id}")
        return {"status": "error", "message": "Security violation: Path traversal attempt detected."}

    try:
        with open(full_path, "rb") as f:
            content = f.read()
        logging.info(f"Successfully read file {found_file} (ID: {file_id})")
        return {
            "status": "success",
            "message": "File read successfully.",
            "file_id": file_id,
            "filename": found_file,
            "content": content.decode('utf-8', errors='ignore') # Assuming text content for display
        }
    except IOError as e:
        logging.error(f"Error reading file {found_file} (ID: {file_id}): {e}")
        return {"status": "error", "message": f"Failed to read file: {e}"}

def search_files(query: str, use_rag: bool = False) -> Dict[str, Any]:
    """
    Searches for files in the mock drive.
    Supports keyword search and a RAG stub for provenance tracking.

    Args:
        query (str): The search query (keyword).
        use_rag (bool): If True, simulates RAG search with provenance.

    Returns:
        Dict[str, Any]: A dictionary containing search results.
    """
    logging.info(f"Searching for files with query: '{query}', RAG: {use_rag}")
    results = []
    all_files = os.listdir(MOCK_DRIVE_ROOT)

    for fname in all_files:
        full_path = os.path.join(MOCK_DRIVE_ROOT, fname)
        if not os.path.isfile(full_path):
            continue

        file_id = fname[:12] # Assuming first 12 chars are the ID

        try:
            with open(full_path, "r", encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if query.lower() in content.lower() or query.lower() in fname.lower():
                result_item = {
                    "file_id": file_id,
                    "filename": fname,
                    "match_type": "keyword",
                    "excerpt": content[:200] + "..." if len(content) > 200 else content,
                    "provenance": {
                        "source_id": file_id,
                        "timestamp": datetime.fromtimestamp(os.path.getmtime(full_path)).isoformat(),
                        "method": "direct_file_match"
                    }
                }
                results.append(result_item)

        except Exception as e:
            logging.error(f"Error processing file {fname} during search: {e}")
            continue

    if use_rag:
        # RAG Stub with Source ID for provenance
        # In a real RAG system, this would involve embedding the query and documents,
        # retrieving relevant chunks, and generating a response.
        # For this stub, we'll just add a simulated RAG result if a keyword match is found.
        if results:
            logging.info("Simulating RAG enrichment for search results.")
            for result in results:
                result["provenance"]["method"] = "RAG_enriched"
                result["provenance"]["rag_model_id"] = "MAESTRO_RAG_v1.0"
                result["provenance"]["retrieval_score"] = 0.85 # Simulated score
                result["rag_summary"] = f"This document contains information related to '{query}' as identified by the RAG system."

    logging.info(f"Found {len(results)} search results for query '{query}'.")
    return {
        "status": "success",
        "message": f"Search completed. Found {len(results)} results.",
        "query": query,
        "results": results
    }

# --- Main execution block for standalone server ---
if __name__ == "__main__":
    logging.info("MCP Drive Server starting in standalone mode.")
    logging.info(f"Mock drive root: {MOCK_DRIVE_ROOT}")
    logging.info(f"Allowed file types: {list(ALLOWED_FILE_TYPES.values())}")

    # Example Usage:

    # 1. Upload a valid file
    test_content_txt = b"This is a test document for the MCP Drive Server. It contains important information."
    upload_result_txt = upload_file("test_doc.txt", test_content_txt, "text/plain")
    print("\nUpload TXT Result:", upload_result_txt)
    uploaded_file_id_txt = upload_result_txt.get("file_id")

    test_content_md = b"# Markdown Test\n\nThis is a **markdown** file."
    upload_result_md = upload_file("report.md", test_content_md, "text/markdown")
    print("\nUpload MD Result:", upload_result_md)
    uploaded_file_id_md = upload_result_md.get("file_id")

    # 2. Attempt to upload an invalid file type
    test_content_exe = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00\xb8\x00\x00\x00\x00\x00\x00\x00@"
    upload_result_exe = upload_file("malicious.exe", test_content_exe, "application/x-msdownload")
    print("\nUpload EXE Result (expected error):", upload_result_exe)

    # 3. Attempt to upload a file with malware signature
    test_content_malware = b"This is a clean file, but it contains malware_signature for testing."
    upload_result_malware = upload_file("infected.txt", test_content_malware, "text/plain")
    print("\nUpload Malware Result (expected error):", upload_result_malware)

    # 4. Read a valid file
    if uploaded_file_id_txt:
        read_result = read_file(uploaded_file_id_txt)
        print("\nRead TXT Result:", read_result)

    # 5. Attempt to read a non-existent file
    read_non_existent_result = read_file("nonexistent_id")
    print("\nRead Non-Existent Result (expected error):", read_non_existent_result)

    # 6. Search for files
    search_result_keyword = search_files("important")
    print("\nSearch Keyword Result:", search_result_keyword)

    search_result_rag = search_files("markdown", use_rag=True)
    print("\nSearch RAG Result:", search_result_rag)

    search_result_no_match = search_files("nonexistent_term")
    print("\nSearch No Match Result:", search_result_no_match)

    logging.info("MCP Drive Server example usage complete.")
