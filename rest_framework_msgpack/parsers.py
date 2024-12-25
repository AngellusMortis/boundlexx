import decimal
import msgpack
from dateutil.parser import parse
from six import text_type


from rest_framework.parsers import BaseParser
from rest_framework.exceptions import ParseError


class MessagePackDecoder(object):

    def decode(self, obj):
        if '__class__' in obj:
            decode_func = getattr(self, 'decode_%s' % obj['__class__'])
            return decode_func(obj)
        return obj

    def decode_datetime(self, obj):
        return parse(obj['as_str'])

    def decode_date(self, obj):
        return parse(obj['as_str']).date()

    def decode_time(self, obj):
        return parse(obj['as_str']).time()

    def decode_decimal(self, obj):
        return decimal.Decimal(obj['as_str'])


class MessagePackParser(BaseParser):
    """
    Parses MessagePack-serialized data.
    """

    media_type = 'application/msgpack'

    def _clean_msgpack_value(self, value, lookup):
        if isinstance(value, (dict, list)):
            value = _map_msgpack(value, lookup)
        elif isinstance(value, str):
            value = value.replace("\u0000", "")

        return value


    def _map_msgpack(self, unmapped, lookup):
        mapped: Optional[Union[list, dict]] = None
        if isinstance(unmapped, dict):
            mapped = {}

            for key, value in unmapped.items():
                value = _clean_msgpack_value(value, lookup)
                mapped[lookup[key]] = value
        elif isinstance(unmapped, list):
            mapped = []
            for value in unmapped:
                value = _clean_msgpack_value(value, lookup)
                mapped.append(value)
        else:
            raise Exception("Unknown unmapped object")

        return mapped


    def parse(self, stream, media_type=None, parser_context=None):
        try:
            root, lookup = msgpack.load(
                stream, encoding="utf-8", object_hook=MessagePackDecoder().decode
            )
            return self._map_msgpack(root, lookup)
        except Exception as exc:
            raise ParseError('MessagePack parse error - %s' % text_type(exc))
