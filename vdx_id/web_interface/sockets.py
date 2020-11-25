from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

_CHANNEL_LAYER = None


def get_channel():
    global _CHANNEL_LAYER
    if _CHANNEL_LAYER is None:
        _CHANNEL_LAYER = get_channel_layer()
    return _CHANNEL_LAYER


def send_notification(**payload):
    channel = get_channel()
    payload["type"] = "notification"
    async_to_sync(channel.group_send)(
        'notifications', payload)

def send_map_update(map_flow_arr):
    channel = get_channel()
    payload = {
        "type": "map_update",
        "flows": map_flow_arr
    }
    async_to_sync(channel.group_send)(
        'map_update', payload)