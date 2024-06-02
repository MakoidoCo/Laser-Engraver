import logging
from serial.tools import list_ports
import serial
import colorlog

# Configure logging with colorlog
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(reset)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

# Handlers
file_handler = logging.FileHandler("usb_device_detector.log", mode='w')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, stream_handler])

class USBDeviceDetector:
    def __init__(self):
        """Initialize USBDeviceDetector."""
        logging.debug("Initializing USBDeviceDetector...")
        self.ser = None
        self.connected_devices = list()
        self.brands = ["wch.cn"]
        self.baudrates = [300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        logging.debug("Initialization complete.")

    def detect_devices(self):
        """Detect all connected USB devices and store their information."""
        logging.debug("Detecting connected USB devices...")
        self.connected_devices = list()
        ports = list_ports.comports()

        for port in ports:
            logging.debug(f"Inspecting port: {port.device}")
            if port.device:
                device_info = {
                    "device": port.device,
                    "name": port.name,
                    "description": port.description,
                    "hwid": port.hwid,
                    "vid": port.vid,
                    "pid": port.pid,
                    "serial_number": port.serial_number,
                    "location": port.location,
                    "manufacturer": port.manufacturer,
                    "product": port.product,
                    "interface": port.interface,
                }
                if device_info["manufacturer"] in self.brands:
                    self.connected_devices.append(device_info)
        logging.info("Detected devices: %s", self.connected_devices)

    def get_connected_devices(self):
        """Return a list of connected USB devices."""
        logging.debug("Getting list of connected USB devices.")
        return self.connected_devices

    def print_connected_devices(self):
        """Print detailed information about connected USB devices."""
        if self.connected_devices:
            logging.info("Connected Devices:")
            for device in self.connected_devices:
                device_info = (
                    f"Device: {device['device']}\n"
                    f"  Name: {device['name']}\n"
                    f"  Description: {device['description']}\n"
                    f"  HWID: {device['hwid']}\n"
                    f"  VID: {device['vid']}\n"
                    f"  PID: {device['pid']}\n"
                    f"  Serial Number: {device['serial_number']}\n"
                    f"  Location: {device['location']}\n"
                    f"  Manufacturer: {device['manufacturer']}\n"
                    f"  Product: {device['product']}\n"
                    f"  Interface: {device['interface']}\n"
                )
                logging.info(device_info)
        else:
            logging.info("No devices connected.")

    def try_connect(self):
        """Try to connect to each device using the provided baudrates."""
        logging.debug("Attempting to connect to devices...")
        for device in self.connected_devices:
            port = device["device"]
            if device["manufacturer"] == "Microsoft":
                logging.debug(f"Skipping device {port} (Microsoft device).")
                continue
            for baudrate in self.baudrates:
                try:
                    logging.info("Attempting connection to %s with baudrate %d", port, baudrate)
                    self.ser = serial.Serial(port, baudrate, timeout=2)
                    self.ser.write(f"$I\n".encode())
                    response = self.ser.read_until()

                    try:
                        decoded_response = response.decode()
                        logging.info("Response from %s at %d: %s", port, baudrate, decoded_response)
                    except UnicodeDecodeError:
                        logging.warning("Received non-UTF-8 response from %s at %d: %s", port, baudrate, response)
                        continue

                    if response:
                        logging.info("Successfully connected on %s at %d.", port, baudrate)
                        return port, baudrate
                except (serial.SerialException, serial.SerialTimeoutException, PermissionError) as e:
                    logging.error("Failed to connect to %s at %d: %s", port, baudrate, e)
                finally:
                    if self.ser and self.ser.is_open:
                        logging.debug(f"Closing connection to {port}.")
                        self.ser.close()
                        self.ser = None
        logging.error("Couldn't connect to any device.")
        return None, None

if __name__ == "__main__":
    detector = USBDeviceDetector()
    detector.detect_devices()
    detector.print_connected_devices()
    detector.try_connect()
