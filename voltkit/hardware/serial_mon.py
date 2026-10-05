"""
Serial / COM port scanner and live terminal monitor for microcontrollers.
"""
import sys
import time
from typing import List, Optional
import serial.tools.list_ports
from rich.table import Table
from voltkit.utils.formatting import console, print_error, print_info, print_success

def list_com_ports():
    """Lists all available serial / COM ports with details."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print_info("No active COM / Serial ports detected.")
        return []

    table = Table(title="[SERIAL] Available Serial / COM Ports", header_style="bold magenta", border_style="dim cyan")
    table.add_column("Port", justify="center", style="bold cyan", width=10)
    table.add_column("Description", style="white", width=36)
    table.add_column("Hardware ID / Details", style="yellow", width=38)

    for p in ports:
        table.add_row(
            p.device,
            p.description or "Generic Serial Port",
            p.hwid or "-"
        )

    console.print(table)
    return ports

def monitor_serial(port: str, baudrate: int = 115200, hex_mode: bool = False):
    """Simple live serial monitor with Ctrl+C exit."""
    import serial
    print_info(f"Opening {port} at {baudrate} baud... (Press Ctrl+C to disconnect)")
    try:
        ser = serial.Serial(port, baudrate, timeout=0.1)
        print_success(f"Connected to {port} successfully!")
        
        while True:
            try:
                line = ser.readline()
                if line:
                    if hex_mode:
                        hex_str = " ".join(f"{b:02X}" for b in line)
                        console.print(f"[dim cyan]{time.strftime('%H:%M:%S')}[/dim cyan] [yellow]{hex_str}[/yellow]")
                    else:
                        text = line.decode('utf-8', errors='replace').rstrip('\r\n')
                        console.print(f"[dim cyan]{time.strftime('%H:%M:%S')}[/dim cyan] {text}")
            except KeyboardInterrupt:
                break
    except serial.SerialException as e:
        print_error(f"Could not open {port}: {e}")
    finally:
        try:
            ser.close()
        except Exception:
            pass
        print_info("Serial connection closed.")
