import json
from enum import Enum


class PrcocessStatus(Enum):
    Processing = "Processing"
    Finished = "Finished"


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value  # 或者 obj.value
        return json.JSONEncoder.default(self, obj)
