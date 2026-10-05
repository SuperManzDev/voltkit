"""
VoltKit Command Line Interface (CLI)
"""
import click
from voltkit.utils.formatting import print_banner
from voltkit.hardware.usb import display_usb_table
from voltkit.hardware.serial_mon import list_com_ports, monitor_serial
from voltkit.hardware.adb_helper import display_adb_devices, take_adb_screenshot
from voltkit.rev.hexview import hex_dump
from voltkit.rev.strings import display_strings
from voltkit.rev.entropy import display_entropy_map
from voltkit.rev.converter import convert_value
from voltkit.tui import run_tui_loop

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """VoltKit: Embedded Dev, Hardware & Reverse Engineering Toolkit."""
    if ctx.invoked_subcommand is None:
        run_tui_loop()

@main.command()
@click.option("--embedded", "-e", is_flag=True, help="Show only embedded & microcontroller targets.")
def usb(embedded):
    """List connected USB devices with hardware & vendor identification."""
    display_usb_table(embedded_only=embedded)

@main.command()
@click.option("--port", "-p", default=None, help="COM port to monitor (e.g. COM3).")
@click.option("--baud", "-b", default=115200, type=int, help="Baud rate (default: 115200).")
@click.option("--hex", "hex_mode", is_flag=True, help="Display incoming bytes in hex.")
def serial(port, baud, hex_mode):
    """Scan available COM ports or start a live serial monitor."""
    if not port:
        list_com_ports()
    else:
        monitor_serial(port, baud, hex_mode=hex_mode)

@main.command()
@click.option("--screenshot", "-s", default=None, help="Capture screenshot from active device.")
def adb(screenshot):
    """Manage connected Android/ADB devices or take a screenshot."""
    if screenshot:
        take_adb_screenshot(screenshot)
    else:
        display_adb_devices()

@main.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--offset", "-o", default="0x0", help="Starting byte offset (hex or dec).")
@click.option("--length", "-n", default=256, type=int, help="Number of bytes to display.")
@click.option("--search", "-s", default=None, help="Highlight search pattern.")
def hex(filepath, offset, length, search):
    """Inspect binary files with colorized hex and ASCII."""
    off = int(offset, 16) if offset.lower().startswith("0x") else int(offset)
    hex_dump(filepath, offset=off, length=length, search=search)

@main.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--min-len", "-m", default=4, type=int, help="Minimum string length.")
@click.option("--filter", "-f", "pat_filter", default=None, help="Regex / text filter.")
@click.option("--limit", "-l", default=100, type=int, help="Max results to display.")
def strings(filepath, min_len, pat_filter, limit):
    """Extract ASCII and UTF-16 strings from binary files."""
    display_strings(filepath, min_len=min_len, pattern_filter=pat_filter, max_results=limit)

@main.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--block-size", "-b", default=1024, type=int, help="Block size for entropy calculation.")
def entropy(filepath, block_size):
    """Analyze Shannon entropy map of firmware or binary files."""
    display_entropy_map(filepath, block_size=block_size)

@main.command()
@click.argument("value")
def conv(value):
    """Convert and deconstruct values across hex, int, binary, floats, and endianness."""
    convert_value(value)

if __name__ == "__main__":
    main()
