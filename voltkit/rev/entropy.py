"""
Shannon Entropy Analyzer for firmware and binary reverse engineering.
Identifies encrypted, compressed, code, and padding sections.
"""
import os
import math
from typing import List, Tuple
from rich.table import Table
from rich.panel import Panel
from voltkit.utils.formatting import console, print_error, print_info

def calculate_entropy(data: bytes) -> float:
    """Calculates Shannon entropy of a byte chunk (0.0 to 8.0)."""
    if not data:
        return 0.0
    length = len(data)
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    entropy = 0.0
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def analyze_firmware_entropy(file_path: str, block_size: int = 1024) -> List[Tuple[int, float, str]]:
    """Analyzes a file in blocks and returns (offset, entropy, category)."""
    if not os.path.isfile(file_path):
        print_error(f"File not found: {file_path}")
        return []

    file_size = os.path.getsize(file_path)
    results = []

    with open(file_path, "rb") as f:
        offset = 0
        while offset < file_size:
            chunk = f.read(block_size)
            if not chunk:
                break
            ent = calculate_entropy(chunk)
            
            if ent > 7.3:
                cat = "[bold red]Encrypted / Packed[/bold red]"
            elif ent > 5.2:
                cat = "[bold yellow]Executable Code (ARM/x86)[/bold yellow]"
            elif ent > 2.8:
                cat = "[bold cyan]Data / Text / Tables[/bold cyan]"
            elif ent > 0.5:
                cat = "[blue]Sparse Data[/blue]"
            else:
                cat = "[dim white]Padding / Zeroes[/dim white]"

            results.append((offset, ent, cat))
            offset += len(chunk)

    return results

def display_entropy_map(file_path: str, block_size: int = 1024, max_blocks: int = 35):
    """Displays a graphical entropy bar representation of the binary."""
    results = analyze_firmware_entropy(file_path, block_size)
    if not results:
        return

    file_size = os.path.getsize(file_path)
    console.print(Panel(
        f"File: [bold white]{os.path.basename(file_path)}[/bold white] | Size: [yellow]{file_size:,} bytes[/yellow] | Block Size: [cyan]{block_size} bytes[/cyan]",
        title="[ENTROPY] Firmware Entropy Analyzer",
        border_style="magenta"
    ))

    step = max(1, len(results) // max_blocks)
    sampled = results[::step]

    table = Table(header_style="bold magenta", border_style="dim cyan")
    table.add_column("Offset", justify="right", style="cyan", width=12)
    table.add_column("Entropy", justify="right", style="white", width=8)
    table.add_column("Visual Map", width=34)
    table.add_column("Suspected Content", width=28)

    for offset, ent, cat in sampled:
        bar_len = int((ent / 8.0) * 28)
        
        if ent > 7.3:
            color = "red"
        elif ent > 5.2:
            color = "yellow"
        elif ent > 2.8:
            color = "cyan"
        else:
            color = "blue"

        bar = f"[{color}]{'#' * bar_len}{'.' * (28 - bar_len)}[/{color}]"

        table.add_row(
            f"0x{offset:08X}",
            f"{ent:.2f}",
            bar,
            cat
        )

    console.print(table)
    console.print("[dim]Key: [red]# Encrypted/Compressed (>7.3)[/red] | [yellow]# Code (5.2-7.3)[/yellow] | [cyan]# Tables/Data (2.8-5.2)[/cyan] | [blue]# Padding (<2.8)[/blue][/dim]\n")
