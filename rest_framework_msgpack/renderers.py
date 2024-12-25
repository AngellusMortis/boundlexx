import datetime
import decimal
from collections.abc import Iterable, Mapping

import msgpack
from rest_framework.renderers import BaseRenderer


class MessagePackEncoder(object):
    def encode(self, obj):
        if isinstance(obj, datetime.datetime):
            return {"__class__": "datetime", "as_str": obj.isoformat()}
        elif isinstance(obj, datetime.date):
            return {"__class__": "date", "as_str": obj.isoformat()}
        elif isinstance(obj, datetime.time):
            return {"__class__": "time", "as_str": obj.isoformat()}
        elif isinstance(obj, decimal.Decimal):
            return {"__class__": "decimal", "as_str": str(obj)}
        else:
            return obj


class MessagePackRenderer(BaseRenderer):
    """
    Renderer which serializes to MessagePack.
    """

    media_type = "application/msgpack"
    format = "msgpack"
    render_style = "binary"
    charset = None

    def _iterate_iterable(self, data, data_map):
        # many iterable types are not mutatable
        if not isinstance(data, list):
            data = list(data)

        for index, value in enumerate(data):
            if isinstance(value, (Mapping, Iterable)) and not isinstance(value, str):
                value, data_map = self._create_mapped_data(value, data_map=data_map)
            data[index] = value

        return data, data_map

    def _iterate_dict(self, data, data_map):
        new_data = {}
        for key, value in data.items():
            if isinstance(value, (Mapping, Iterable)) and not isinstance(value, str):
                value, data_map = self._create_mapped_data(value, data_map=data_map)

            try:
                new_key = data_map.index(key)
            except ValueError:
                new_key = len(data_map)
                data_map.append(key)

            new_data[new_key] = value
        return new_data, data_map

    def _create_mapped_data(self, data, data_map=None):
        if data_map is None:
            data_map = []

        if isinstance(data, Mapping):
            data, data_map = self._iterate_dict(data, data_map)
        elif isinstance(data, Iterable) and not isinstance(data, str):
            data, data_map = self._iterate_iterable(data, data_map)

        return data, data_map

    def render(self, data, media_type=None, renderer_context=None):
        """
        Renders *obj* into serialized MessagePack.
        """
        if data is None:
            return ""

        root, data_map = self._create_mapped_data(data)
        return msgpack.packb([root, data_map], default=MessagePackEncoder().encode)
