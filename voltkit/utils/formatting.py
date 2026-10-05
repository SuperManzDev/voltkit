"""
Styling and formatting helpers for VoltKit using Rich.
"""
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Ensure standard streams handle unicode without dying on cp1252
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

console = Console(highlight=False)

BANNER = r"""
[bold cyan]╦  ╦  ╔═╗  ╦    ╔╦╗  ╦╔═  ╦  ╔╦╗[/bold cyan]
[bold cyan]╚╗╔╝  ║ ║  ║     ║   ╠╩╗  ║   ║ [/bold cyan]
[bold cyan] ╚╝   ╚═╝  ╩═╝   ╩   ╩ ╩  ╩   ╩ [/bold cyan]
[bold yellow]>> Hardware & Reverse Engineering Toolkit <<[/bold yellow]
"""

def print_banner():
    """Prints the styled VoltKit banner."""
    console.print(Panel.fit(BANNER.strip(), border_style="cyan", padding=(0, 2)))

def format_hex_addr(addr: int, width: int = 8) -> str:
    """Formats an address with leading zeros and cyan highlight."""
    return f"[cyan]0x{addr:0{width}X}[/cyan]"

def print_error(msg: str):
    console.print(f"[bold red][X] Error:[/bold red] {msg}")

def print_success(msg: str):
    console.print(f"[bold green][+][/bold green] {msg}")

def print_info(msg: str):
    console.print(f"[bold blue][*][/bold blue] {msg}")

def print_warning(msg: str):
    console.print(f"[bold yellow][!][/bold yellow] {msg}")
