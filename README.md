# VoltKit ⚡

A high-performance Python CLI / TUI toolkit tailored for embedded systems development, hardware hacking, and binary reverse engineering on Windows.

---

## 🚀 Quick Start

Run the interactive dashboard:
```powershell
volt
# or
voltkit
```

Or execute fast one-liner commands directly from your terminal:

```powershell
# 1. Hardware & USB Devices
volt usb                     # List all USB devices with vendor/hardware identification
volt usb --embedded          # Filter for embedded targets (ST, TI, RPi, ESP, FTDI, WCH, etc.)

# 2. Serial & COM Ports
volt serial                  # List active COM ports and hardware IDs
volt serial -p COM3 -b 115200 # Open live serial monitor (Ctrl+C to exit)
volt serial -p COM3 --hex    # Stream incoming serial bytes in hex format

# 3. Android / ADB Dev Tools
volt adb                     # List connected ADB devices & status
volt adb -s screen.png       # Capture and pull screenshot directly to PC

# 4. Binary Hex Inspection
volt hex firmware.bin        # Colorized hex dump with magic header detection
volt hex firmware.bin -o 0x1000 -n 128  # Offset 0x1000, 128 bytes
volt hex firmware.bin -s "Zehn"         # Highlight matching text/hex pattern

# 5. String Extractor
volt strings firmware.bin              # Extract ASCII & UTF-16LE strings with offsets
volt strings firmware.bin -m 6 -f USB  # Min length 6, filtered by regex "USB"

# 6. Firmware Entropy Analyzer
volt entropy firmware.bin    # Shannon entropy map to spot encrypted vs code sections

# 7. Endianness & Value Deconstructor
volt conv 0xDEADBEEF         # Break down into LE/BE, Float32/64, binary nibbles, bits, CRC32
volt conv 12345678
```

---

## 🛠 Features

* **Embedded Hardware ID Database**: Automatically recognizes vendor IDs for STMicroelectronics (STM32), Raspberry Pi (RP2040/RP2350), Espressif (ESP32), Texas Instruments (MSP430/Nspire), FTDI, WCH (CH340), Silicon Labs (CP210x), SEGGER (J-Link), Microchip, Apple DFU, and Google ADB.
* **Shannon Entropy Visualization**: Calculates $H = -\sum p_i \log_2(p_i)$ per block across binary files to instantly distinguish code, tables, encrypted payloads, and empty padding.
* **Multi-Format Value Converter**: Instant bitfield, endianness (LE/BE), IEEE-754 single/double precision floats, ASCII, and CRC32 checksums.
* **Cross-Console Compatibility**: Built with Rich styling optimized for Windows PowerShell and Windows Terminal.
