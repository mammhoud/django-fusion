import json
from collections.abc import Mapping
from typing import Any

from django.http import HttpRequest
from ninja.renderers import BaseRenderer
from ninja.responses import NinjaJSONEncoder

from .responses import *


class JSONRenderer(BaseRenderer):
    media_type = "application/json"
    encoder_class: type[json.JSONEncoder] = NinjaJSONEncoder
    json_dumps_params: Mapping[str, Any] = {}

    def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
        info_message = response_status in codes_1xx
        success = response_status in codes_2xx
        redirect_message = response_status in codes_3xx
        client_error = response_status in codes_4xx
        server_error = response_status in codes_5xx

        if success:
            message = "Success"
        elif client_error:
            message = "Client Error"
        elif server_error:
            message = "Server Error"
        elif redirect_message:
            message = "Redirect"
        elif info_message:
            message = "Informational"
        else:
            message = "Unknown Status"

        response_data = {
            "status": response_status,
            "message": message,
            "data": data,
        }
        return json.dumps(
            response_data, cls=self.encoder_class, **self.json_dumps_params
        )


class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=4, sort_keys=True, **kwargs)
