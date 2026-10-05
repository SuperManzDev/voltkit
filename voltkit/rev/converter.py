"""
Multi-format Value & Endianness Converter for Reverse Engineering.
"""
import struct
import zlib
from rich.table import Table
from rich.panel import Panel
from voltkit.utils.formatting import console, print_error

def convert_value(val_str: str):
    """Parses and breaks down any integer, hex, float, or string."""
    val_str = val_str.strip()
    
    num = None
    try:
        if val_str.lower().startswith("0x"):
            num = int(val_str, 16)
        elif val_str.lower().startswith("0b"):
            num = int(val_str, 2)
        elif val_str.startswith("'") and val_str.endswith("'") and len(val_str) > 2:
            num = int.from_bytes(val_str[1:-1].encode('ascii', errors='replace'), 'big')
        else:
            num = int(val_str)
    except ValueError:
        pass

    if num is None:
        print_error(f"Cannot parse '{val_str}' as integer, hex, or binary literal.")
        return

    bit_length = max(32, num.bit_length())
    byte_width = (bit_length + 7) // 8
    if byte_width in (3, 4):
        byte_width = 4
    elif byte_width in (5, 6, 7, 8):
        byte_width = 8

    mask = (1 << (byte_width * 8)) - 1
    u_val = num & mask

    sign_bit = 1 << ((byte_width * 8) - 1)
    if u_val & sign_bit:
        s_val = u_val - (1 << (byte_width * 8))
    else:
        s_val = u_val

    be_bytes = u_val.to_bytes(byte_width, 'big')
    le_bytes = u_val.to_bytes(byte_width, 'little')

    bin_raw = f"{u_val:0{byte_width*8}b}"
    nibbles = [bin_raw[i:i+4] for i in range(0, len(bin_raw), 4)]
    bin_formatted = " ".join(nibbles)

    active_bits = [i for i in range(byte_width * 8) if (u_val & (1 << i))]

    float32_str = "N/A"
    float64_str = "N/A"
    if byte_width == 4:
        try:
            f32 = struct.unpack(">f", be_bytes)[0]
            float32_str = f"{f32:.8g}"
        except Exception:
            pass
    elif byte_width == 8:
        try:
            f64 = struct.unpack(">d", be_bytes)[0]
            float64_str = f"{f64:.12g}"
        except Exception:
            pass

    ascii_repr = "".join(chr(b) if 32 <= b <= 126 else "." for b in be_bytes)
    crc32_val = zlib.crc32(be_bytes) & 0xFFFFFFFF

    table = Table(title=f"[CONV] Value Breakdown: {val_str}", header_style="bold cyan", border_style="dim cyan")
    table.add_column("Representation", style="bold yellow", width=22)
    table.add_column("Value", style="bold white")

    table.add_row("Hexadecimal (BE)", f"0x{u_val:0{byte_width*2}X}")
    table.add_row("Hexadecimal (LE)", f"0x{''.join(f'{b:02X}' for b in le_bytes)}")
    table.add_row("Unsigned Decimal", f"{u_val:,}")
    table.add_row("Signed Decimal", f"{s_val:,}")
    table.add_row("Binary (Nibbles)", f"[cyan]{bin_formatted}[/cyan]")
    table.add_row("Big-Endian Bytes", " ".join(f"{b:02X}" for b in be_bytes))
    table.add_row("Little-Endian Bytes", " ".join(f"{b:02X}" for b in le_bytes))
    table.add_row("ASCII Text", f"[green]\"{ascii_repr}\"[/green]")
    if byte_width == 4:
        table.add_row("IEEE-754 Float32", float32_str)
    elif byte_width == 8:
        table.add_row("IEEE-754 Float64", float64_str)
    table.add_row("Active Bit Indices", f"[dim cyan]{active_bits}[/dim cyan]")
    table.add_row("CRC32 Checksum", f"0x{crc32_val:08X}")

    console.print(table)
    console.print()
