from rest_framework import serializers
from models import DeviceStatus
from models import HomeDeviceStatus

class DeviceStatusSerializer(serializers.Serializer):
    
    def __init__(self, device_id, status_map):
        self.device_id = device_id
        self.status = status # hash table of status by minute. can 0 (off) or 1(on)


