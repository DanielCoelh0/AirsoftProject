from .mock_hardware import MockHardware
from .rpi_hardware import RpiHardware
import platform

def get_hardware():
    # Simple formatting check: if on Windows, use Mock
    if platform.system() == "Windows":
        return MockHardware()
    else:
        # Assuming Linux is the Pi
        # Could also check /proc/cpuinfo or try-import
        return RpiHardware()
