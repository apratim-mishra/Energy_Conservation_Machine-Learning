
class DeviceStatus(object):
    def __init__(self, device_id, status_map):
        self.device_id = device_id
        self.status = status # hash table of status by minute. can 0 (off) or 1(on)

class HomeDeviceStatus(object):
    def __init__(self, home_id, visible_devices):
        self.home_id = home_id
        self.visible_devices = visible_devices # hash table of DeviceStatus
        
