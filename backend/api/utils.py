from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def broadcast_to_dashboard(data_type, data):
    """Send real-time update to all connected dashboard WebSocket clients."""
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "dashboard",
            {
                "type": "dashboard_update",
                "data_type": data_type,
                "data": data,
            }
        )
    except Exception:
        pass  # Don't fail if no WebSocket clients connected
