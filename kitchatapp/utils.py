from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

def notify_new_message(user_id, message_data):
    """
    Send notification to a specific user via WebSocket
    
    Args:
        user_id: The ID of the user to notify
        message_data: Dict containing message information
    """
    channel_layer = get_channel_layer()
    
    # Convert any non-serializable objects to strings
    serializable_data = json.loads(json.dumps(message_data, default=str))
    
    # Send to the user's notification group
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}_notifications",  # Channel group name for the user
        {
            "type": "notification_message",  # This corresponds to a method in your consumer
            "message": serializable_data
        }
    )
import random
import string

def generate_random_string(length=8):
    """Generate a random alphanumeric string with symbols"""
    chars = string.ascii_letters + string.digits + '-_'
    return ''.join(random.choice(chars) for _ in range(length))