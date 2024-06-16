import logging, serial, os, sys
from serial.tools import list_ports

sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from Config.setup import *

usb_detector_log = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
usb_detector_log.addHandler(HANDLER)
usb_detector_log.setLevel(LOGLEVEL)


class USBDeviceDetector:
    def __init__(self) -> None:
        """Initialize USBDeviceDetector."""
        usb_detector_log.debug("Initializing USBDeviceDetector...")
        self.ser = None
        self.brands = ["wch.cn"]
        self.connected_devices = list()
        self.baudrates = [300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        usb_detector_log.debug("Initialization complete.")


    def run(self) -> None:
        self.__detect_devices()
        self.__print_connected_devices()
        return self.__try_connect()


    def __detect_devices(self) -> None:
        """Detect all connected USB devices and store their information."""
        usb_detector_log.debug("Detecting connected USB devices...")
        self.connected_devices = list()
        ports = list_ports.comports()

        for port in ports:

            usb_detector_log.debug(f"Inspecting port: {port.device}")
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

        usb_detector_log.info("Detected devices: %s", self.connected_devices)


    def __get_connected_devices(self) -> list[int]:
        """Return a list of connected USB devices."""
        usb_detector_log.debug("Getting list of connected USB devices.")
        return self.connected_devices


    def __print_connected_devices(self) -> None:
        """Print detailed information about connected USB devices."""
        if self.connected_devices:
            usb_detector_log.info("Connected Devices:")

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
                usb_detector_log.info(device_info)

        else:
            usb_detector_log.info("No devices connected.")


    def __try_connect(self) -> list[str, int] | list[None, None]:
        """Try to connect to each device using the provided baudrates."""
        usb_detector_log.debug("Attempting to connect to devices...")

        for device in self.connected_devices:
            port = device["device"]

            if device["manufacturer"] == "Microsoft":
                usb_detector_log.debug(f"Skipping device {port} (Microsoft device).")
                continue

            for baudrate in self.baudrates:
                try:
                    usb_detector_log.info("Attempting connection to %s with baudrate %d", port, baudrate)
                    self.ser = serial.Serial(port, baudrate, timeout=2)
                    self.ser.write(f"$I\n".encode())
                    response = self.ser.read_until()

                    try:
                        decoded_response = response.decode()
                        usb_detector_log.info("Response from %s at %d: %s", port, baudrate, decoded_response)

                    except UnicodeDecodeError:
                        usb_detector_log.warning("Received non-UTF-8 response from %s at %d: %s", port, baudrate, response)
                        continue

                    if response:
                        usb_detector_log.info("Successfully connected on %s at %d.", port, baudrate)
                        return port, baudrate
                    
                except (serial.SerialException, serial.SerialTimeoutException, PermissionError) as e:
                    usb_detector_log.error("Failed to connect to %s at %d: %s", port, baudrate, e)

                finally:
                    if self.ser and self.ser.is_open:
                        usb_detector_log.debug(f"Closing connection to {port}.")
                        self.ser.close()
                        self.ser = None
        usb_detector_log.error("Couldn't connect to any device.")

        return None, None


if __name__ == "__main__":
    detector = USBDeviceDetector()
    port, baudrate = detector.run()