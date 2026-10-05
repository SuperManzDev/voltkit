"""
Colorized Hex Viewer & Binary Inspection Tool for VoltKit.
"""
import os
import re
from typing import Optional
from rich.text import Text
from rich.panel import Panel
from voltkit.utils.formatting import console, print_error, print_info

KNOWN_MAGIC = {
    b"\x7fELF": "ELF Binary (Linux/Embedded)",
    b"MZ": "PE Executable (Windows DOS/PE)",
    b"PK\x03\x04": "ZIP / APK / JAR Archive",
    b"\x1f\x8b": "GZIP Compressed File",
    b"7z\xbc\xaf\x27\x1c": "7-Zip Archive",
    b"\x89PNG\r\n\x1a\n": "PNG Image",
    b"\xff\xd8\xff": "JPEG Image",
    b"ZEHN": "TI-Nspire Zehn Relocatable Binary",
    b"Zehn": "TI-Nspire Zehn Relocatable Binary",
    b"*\x00\x00\x00": "TNS Document / TI-Nspire File",
    b"UBI#": "UBIFS / NAND Flash Image",
    b"\x27\x05\x19\x56": "U-Boot Legacy Image",
    b"\xd0\x0d\xfe\xed": "Flattened Device Tree (DTB)"
}

def detect_magic(header_bytes: bytes) -> Optional[str]:
    """Detects file format magic headers."""
    for magic, desc in KNOWN_MAGIC.items():
        if header_bytes.startswith(magic):
            return desc
    return None

def hex_dump(
    file_path: str,
    offset: int = 0,
    length: int = 256,
    search: Optional[str] = None
):
    """Displays a colorized hex dump of the target binary file."""
    if not os.path.isfile(file_path):
        print_error(f"File not found: {file_path}")
        return

    file_size = os.path.getsize(file_path)
    if offset >= file_size:
        print_error(f"Offset 0x{offset:X} is beyond file size ({file_size} bytes).")
        return

    search_bytes = None
    if search:
        if search.startswith("0x"):
            try:
                search_bytes = bytes.fromhex(search[2:])
            except ValueError:
                search_bytes = search.encode('utf-8')
        else:
            search_bytes = search.encode('utf-8')

    with open(file_path, "rb") as f:
        f.seek(offset)
        data = f.read(length)

    magic_desc = detect_magic(data) if offset == 0 else None
    
    header_info = f"File: [bold white]{os.path.basename(file_path)}[/bold white] | Size: [yellow]{file_size:,} bytes[/yellow]"
    if magic_desc:
        header_info += f" | Format: [bold green]{magic_desc}[/bold green]"
    
    console.print(Panel(header_info, border_style="cyan", title="[HEX] Binary Inspection"))

    # Table header
    console.print("[cyan]  Offset    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F   ASCII Data[/cyan]")
    console.print("[dim cyan]  " + "-" * 8 + "  " + "-" * 23 + "  " + "-" * 23 + "   " + "-" * 16 + "[/dim cyan]")

    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        cur_addr = offset + i

        addr_str = f"[cyan]{cur_addr:08X}[/cyan]"

        hex_parts_1 = []
        hex_parts_2 = []
        ascii_parts = []

        for b_idx, b in enumerate(chunk):
            b_char = chr(b) if 32 <= b <= 126 else "."
            
            # Check if part of search pattern
            is_match = False
            if search_bytes and (search_bytes in chunk):
                m_pos = chunk.find(search_bytes)
                if m_pos <= b_idx < m_pos + len(search_bytes):
                    is_match = True

            if is_match:
                b_hex = f"[black on yellow]{b:02X}[/black on yellow]"
                b_ascii = f"[black on yellow]{b_char}[/black on yellow]"
            elif b == 0:
                b_hex = f"[dim white]00[/dim white]"
                b_ascii = f"[dim white].[/dim white]"
            elif 32 <= b <= 126:
                b_hex = f"[green]{b:02X}[/green]"
                b_ascii = f"[bold green]{b_char}[/bold green]"
            elif b == 0xFF:
                b_hex = f"[red]FF[/red]"
                b_ascii = f"[dim red].[/dim red]"
            else:
                b_hex = f"[yellow]{b:02X}[/yellow]"
                b_ascii = f"[dim yellow].[/dim yellow]"

            if b_idx < 8:
                hex_parts_1.append(b_hex)
            else:
                hex_parts_2.append(b_hex)
            ascii_parts.append(b_ascii)

        while len(hex_parts_1) < 8:
            hex_parts_1.append("  ")
        while len(hex_parts_2) < 8:
            hex_parts_2.append("  ")

        str_1 = " ".join(hex_parts_1)
        str_2 = " ".join(hex_parts_2)
        ascii_str = "".join(ascii_parts)

        console.print(f"  {addr_str}  {str_1}  {str_2}  |{ascii_str}|")

    console.print(f"\n[dim]Showing {len(data)} bytes from offset 0x{offset:X} to 0x{offset + len(data):X}[/dim]\n")
