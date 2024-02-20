import json
import pyqrcode
import io

from config import *
from wifi import WifiManager
from ble_gatt import GATTServer, PORT

from .base_handler import BaseHandler

from log import MeticulousLogger
logger = MeticulousLogger.getLogger(__name__)

class WiFiConfig:
    def __init__(self, mode = None, apName = None, apPassword = None):
        self.mode = mode
        self.apName = apName
        self.apPassword = apPassword

    def __repr__(self):
        return f"WiFiConfiguration(mode='{self.mode}', apName='{self.apName}', apPassword='{self.apPassword}')"

    @classmethod
    def from_json(cls, json_data):
        mode = json_data.get('mode')
        apName = json_data.get('apName')
        apPassword = json_data.get('apPassword')
        return cls(mode, apName, apPassword)

    def to_json(self):
        return {
            "mode": self.mode,
            "apName": self.apName,
            "apPassword": self.apPassword,
        }

class WiFiQRHandler(BaseHandler):
    def get(self):
        config = WifiManager.getCurrentConfig()
        logger.warning(config)
        qr_contents: str = ""
        if config.is_hotspot():
            ssid = MeticulousConfig[CONFIG_WIFI][WIFI_AP_NAME]
            password = MeticulousConfig[CONFIG_WIFI][WIFI_AP_PASSWORD]
            qr_contents = f"WIFI:S:{ssid};T:WPA2;P:{password};H:true;;"
        elif len(config.ips) > 0:
            current_ip = config.ips[0]
            if current_ip.ip.version == 6:
                qr_contents = f"http://[{str(current_ip.ip)}]:{PORT}"
            else:
                qr_contents = f"http://{str(current_ip.ip)}:{PORT}"
        else:
            qr_contents = f"http://{str(config.hostname)}.local:{PORT}"

        buffer = io.BytesIO()

        qr = pyqrcode.create(qr_contents)
        qr.png(buffer, scale=3, quiet_zone=2,
               module_color=[0xFF, 0x00, 0x00, 0xFF],
               background=[0xFF, 0xFF, 0xFF, 0xFF],)

        self.set_header("Content-Type", "image/png")
        self.write(buffer.getvalue())

class WiFiConfigHandler(BaseHandler):
    def get(self):
        mode = MeticulousConfig[CONFIG_WIFI][WIFI_MODE]
        apName = MeticulousConfig[CONFIG_WIFI][WIFI_AP_NAME]
        apPassword = MeticulousConfig[CONFIG_WIFI][WIFI_AP_PASSWORD]
        wifi_config = {
            "config": WiFiConfig(mode, apName, apPassword).to_json(),
            "status": WifiManager.getCurrentConfig().to_json(),
        }
        self.write(json.dumps(wifi_config))

    def post(self):
        try:
            data = json.loads(self.request.body)
            if "provisioning" in data and data["provisioning"] == True:
                logger.warning("Enableing GATT provisioning")
                GATTServer.getServer().allow_wifi_provisioning()
                del data["provisioning"]

            if "mode" in data and data["mode"] in [WIFI_MODE_AP, WIFI_MODE_CLIENT]:
                logger.warning("Changing wifi mode")
                MeticulousConfig[CONFIG_WIFI][WIFI_MODE] = data["mode"]
                MeticulousConfig.save()
                WifiManager.resetWifiMode()
                del data["mode"]

            logger.info(f"Unused request entries: {data}")

            return self.get()
        except json.JSONDecodeError as e:
            self.set_status(400)
            self.write(f"Invalid JSON")
            logger.warning(f"Failed to parse passed JSON: {e}", stack_info=False)

        except Exception as e:
            self.set_status(400)
            self.write(f"Failed to write config")
            logger.warning("Failed to accept passed config: ", exc_info=e, stack_info=True)

class WiFiListHandler(BaseHandler):
    def get(self):
        networks = dict()
        try:
            for s in WifiManager.scanForNetworks():
                if s.ssid is not None and s.ssid != "":
                    formated : dict = {"ssid": s.ssid, "signal": s.signal, "rate": s.rate, "in_use": s.in_use}
                    exists = networks.get(s.ssid)
                    # Make sure the network in use is always listed
                    if exists is None or s.in_use:
                        networks[s.ssid] = formated.copy()
                    else:
                        # Dont overwrite the in_use network
                        logger.warning(f"{exists}, {exists.get('signal')}")
                        if exists["in_use"]:
                            continue
                        if s.signal > exists["signal"]:
                            networks[s.ssid] = formated
            response = sorted(networks.values(), key=lambda x: x["signal"], reverse=True)
            response = json.dumps(response)
            self.write(response)
        except Exception as e:
            self.set_status(400)
            self.write(f"Failed to fetch wifi list")
            logger.warning("Failed to fetch / format wifi list: ", exc_info=e, stack_info=True)

class WiFiConnectHandler(BaseHandler):
    def post(self):
        try:
            data = json.loads(self.request.body)
            ssid = data['ssid']
            password = data['password']

            success = WifiManager.connectToWifi(ssid, password)

            if success:
                self.write("Successfully initiated connection to WiFi network.")
            else:
                self.set_status(400)
                self.write("Failed to conect")
        except Exception as e:
            self.set_status(400)
            self.write(f"Failed to connect")
            logger.warning("Failed to connect: ", exc_info=e, stack_info=True)

WIFI_HANDLER = [
        (r"/wifi/config", WiFiConfigHandler),
        (r"/wifi/config/qr.png", WiFiQRHandler),
        (r"/wifi/list", WiFiListHandler),
        (r"/wifi/connect", WiFiConnectHandler),
    ]
