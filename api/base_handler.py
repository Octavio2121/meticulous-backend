import tornado.ioloop
import tornado.web
from netaddr import IPNetwork

from config import (
    CONFIG_SYSTEM,
    CONFIG_WIFI,
    HTTP_ALLOWED_NETWORKS,
    HTTP_AUTH_KEY,
    WIFI_MODE,
    WIFI_MODE_AP,
    MeticulousConfig,
)


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        # FIXME: I know this is not great, you know this isn't great. What shall we do about this?
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Expose-Headers", "*")

        self.set_header("Content-type", "application/json")
        self.set_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS,DELETE")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        # We hate caching!
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Pragma", "no-cache")
        self.set_header("Expires", "0")

    def report_error(self, error_code, error: str, error_details=None):
        self.set_status(error_code)
        self.write({"error": error, "details": error_details})

    def options(self, *args, **kwargs):
        # No body for OPTIONS requests
        self.set_status(204)
        self.finish()

    def prepare(self):

        return

        # Skip the check if the request is from localhost
        if self.request.remote_ip == "127.0.0.1" and self.request.remote_ip == "::1":
            return

        if MeticulousConfig[CONFIG_WIFI][WIFI_MODE] == WIFI_MODE_AP:
            return

        allowed_networks = [
            IPNetwork(x) for x in MeticulousConfig[CONFIG_SYSTEM][HTTP_ALLOWED_NETWORKS]
        ]

        # TODO test me well!
        if (
            len(
                [
                    network
                    for network in allowed_networks
                    if self.request.remote_ip in network
                ]
            )
            > 0
        ):
            return

        # Validate the X-Authorized header
        x_authorized = self.request.headers.get("X-Authorized")
        if (
            not x_authorized
            or x_authorized != MeticulousConfig[CONFIG_SYSTEM][HTTP_AUTH_KEY]
        ):
            self.set_status(401)
            self.finish("Unauthorized: Missing X-Authorized header")
            return
