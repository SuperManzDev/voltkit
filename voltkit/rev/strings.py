"""
Binary strings extraction utility supporting ASCII & UTF-16LE.
"""
import os
import re
from typing import Optional, List, Tuple
from rich.table import Table
from voltkit.utils.formatting import console, print_error, print_info

ASCII_PATTERN = re.compile(rb"[\x20-\x7E]{4,}")
UTF16_PATTERN = re.compile(rb"(?:[\x20-\x7E]\x00){4,}")

def extract_strings(
    file_path: str,
    min_len: int = 4,
    pattern_filter: Optional[str] = None,
    max_results: int = 100
) -> List[Tuple[int, str, str]]:
    """Extracts strings from file returning (offset, encoding, text)."""
    if not os.path.isfile(file_path):
        print_error(f"File not found: {file_path}")
        return []

    regex_ascii = re.compile(rb"[\x20-\x7E]{" + str(min_len).encode() + rb",}")
    regex_utf16 = re.compile(rb"(?:[\x20-\x7E]\x00){" + str(min_len).encode() + rb",}")

    filter_re = re.compile(pattern_filter, re.IGNORECASE) if pattern_filter else None
    results = []

    with open(file_path, "rb") as f:
        data = f.read()

    # Find ASCII strings
    for m in regex_ascii.finditer(data):
        val = m.group().decode('ascii', errors='ignore')
        if filter_re and not filter_re.search(val):
            continue
        results.append((m.start(), "ASCII", val))
        if len(results) >= max_results:
            break

    # Find UTF-16LE strings
    if len(results) < max_results:
        for m in regex_utf16.finditer(data):
            try:
                val = m.group().decode('utf-16le', errors='ignore')
            except Exception:
                continue
            if filter_re and not filter_re.search(val):
                continue
            results.append((m.start(), "UTF-16", val))
            if len(results) >= max_results:
                break

    results.sort(key=lambda x: x[0])
    return results[:max_results]

def display_strings(file_path: str, min_len: int = 4, pattern_filter: Optional[str] = None, max_results: int = 100):
    """Displays extracted strings in a rich table."""
    results = extract_strings(file_path, min_len, pattern_filter, max_results)
    if not results:
        print_info("No matching strings found.")
        return

    filter_info = f" (filtered: '{pattern_filter}')" if pattern_filter else ""
    table = Table(
        title=f"[STRINGS] Strings in {os.path.basename(file_path)}{filter_info}",
        header_style="bold magenta",
        border_style="dim cyan"
    )
    table.add_column("Offset", justify="right", style="cyan", width=14)
    table.add_column("Encoding", justify="center", style="yellow", width=10)
    table.add_column("Length", justify="right", style="dim", width=8)
    table.add_column("String Content", style="bold white")

    for offset, enc, val in results:
        table.add_row(
            f"0x{offset:08X}",
            enc,
            str(len(val)),
            val
        )

    console.print(table)
    console.print(f"[dim]Showing {len(results)} strings (capped at {max_results})[/dim]\n")
