"""Native observation adapter for the existing QCAL hardware protocol.

Mirrors the serial commands already present in RelojCuantico-141Hz-QCAL's
Arduino Mega / Si5351 firmware: STATUS, I2C_SCAN and ANALOG_READ. No synthetic
signal is produced by this adapter.
"""
from __future__ import annotations
from dataclasses import dataclass
import time
from typing import Optional

F0_QCAL_HZ = 141.7001
SI5351_I2C_ADDR = 0x60
BAUDRATE = 115200

class QCALHardwareError(RuntimeError):
    pass

@dataclass(frozen=True)
class HardwareStatus:
    transport: str
    port: str
    si5351: str
    gsr_raw: Optional[int]
    led: Optional[str]

class SerialQCALHardware:
    """Serial adapter for the existing AURON Mega / Si5351 firmware."""
    def __init__(self, port: str, baudrate: int = BAUDRATE, serial_module=None):
        self.port = port
        self.baudrate = baudrate
        self._serial_module = serial_module
        self._serial = None

    def connect(self) -> None:
        if self._serial_module is None:
            try:
                import serial as serial_module
            except ImportError as exc:
                raise QCALHardwareError("pyserial is required for physical acquisition") from exc
            self._serial_module = serial_module
        self._serial = self._serial_module.Serial(self.port, self.baudrate, timeout=2)
        time.sleep(2)

    def close(self) -> None:
        if self._serial is not None and getattr(self._serial, "is_open", False):
            self._serial.close()

    def _command(self, command: str) -> list[str]:
        if self._serial is None:
            raise QCALHardwareError("hardware is not connected")
        self._serial.write((command + "\n").encode("ascii"))
        lines = []
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            line = self._serial.readline().decode("utf-8", errors="replace").strip()
            if line:
                lines.append(line)
                if line.startswith(("I2C_ACK:", "I2C_NACK:", "ANALOG:", "AMP_OK", "LED_OK:", "FREQ_OK", "FREQ_ERROR", "ERROR:")):
                    break
        return lines

    def status(self) -> HardwareStatus:
        lines = self._command("STATUS")
        si5351 = next((x.split(":", 1)[1] for x in lines if x.startswith("SI5351:")), "UNKNOWN")
        gsr_text = next((x.split(":", 1)[1] for x in lines if x.startswith("GSR:")), None)
        led = next((x.split(":", 1)[1] for x in lines if x.startswith("LED:")), None)
        return HardwareStatus("serial", self.port, si5351, int(gsr_text) if gsr_text is not None else None, led)

    def scan_i2c(self, address: int = SI5351_I2C_ADDR) -> bool:
        return any(line == f"I2C_ACK:0x{address:x}" for line in self._command(f"I2C_SCAN:0x{address:x}"))

    def read_analog(self, pin: str = "A0") -> int:
        for line in self._command(f"ANALOG_READ:{pin}"):
            if line.startswith("ANALOG:"):
                return int(line.split(":", 1)[1])
        raise QCALHardwareError("firmware did not return an ANALOG sample")

    def discover(self) -> dict:
        status = self.status()
        si5351_ack = self.scan_i2c()
        return {
            "source": "RelojCuantico-141Hz-QCAL",
            "transport": "serial",
            "port": self.port,
            "baudrate": self.baudrate,
            "protocol": ["STATUS", "I2C_SCAN", "ANALOG_READ"],
            "si5351_i2c_address": hex(SI5351_I2C_ADDR),
            "si5351_status": status.si5351,
            "si5351_i2c_ack": si5351_ack,
            "nominal_frequency_hz": F0_QCAL_HZ,
            "measurement_mode": "analog acquisition",
        }
