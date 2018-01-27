from pyHS100 import SmartPlug
from pyHS100 import SmartPlugException
import time
plug_devices = {
    'living_room': "xxx.xx.xx.x"
}


class PlugHandler(object):
    def __init__(self):
        self.plug = SmartPlug(plug_devices['living_room'])

    def switch_on(self):
        try:
            if self.plug.state == 'OFF':
                self.plug.turn_on()
                return 'switched on.'
            else:
                return 'already Switched on.'
        except Exception as e:
            print e
            return 'Try Again.'

    def switch_off(self):
        try:
            if self.plug.state == 'ON':
                self.plug.turn_off()
                return 'switched off.'
            else:
                return 'already Switched off.'
        except Exception as e:
            print e
            return 'Try Again.'

# obj = PlugHandler()
# print obj.switch_off()
