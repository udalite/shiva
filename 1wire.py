import subprocess
from subprocess import Popen
import os

class W1Relay():
    """Class to work with DS2408 1Wire chip through w1_ds2408 block device"""
    def __init__(self, w1_id):
        self.w1_path = "/sys/bus/w1/devices/%s/output" % w1_id

    def read_status_int(self):
        cmd = "dd if=%s bs=1 count=1 | hexdump" % self.w1_path
        process = Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = process.stdout.readline().strip()
        status_hex_str = output[-2:]
        status_int = int(status_hex_str, 16)
        return status_int

    def write_status_int(self, new_status_int):
        new_status_hex = hex(new_status_int)[1:]
        cmd = "echo -e \\\\%s | dd of=%s bs=1 count=1" % (new_status_hex, self.w1_path)
        Popen(cmd, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def get_relay_status(self, relay_n):
        status_int = self.read_status_int()
        bit_mask = 1<<relay_n
        return (status_int & bit_mask != 0)

    def on(self, relay_n):
        status_int = self.read_status_int()
        new_status_int = status_int & ~(1<<relay_n)
        self.write_status_int(new_status_int)

    def off(self, relay_n):
        status_int = self.read_status_int()
        new_status_int = status_int | 1<<relay_n
        self.write_status_int(new_status_int)

class W1Thermometer():
    """Class to work with 1wire thermometer"""
    def __init__(self, w1_id):
        self.w1_path = "/sys/bus/w1/devices/%s/w1_slave" % w1_id

    def read_temp(self):
        with open(self.w1_path, "r") as fp:
            lines = fp.readlines()
            if lines[0][-4:-1] == "YES":
                water_temp = int(lines[1][-6:-1])
                water_temp = water_temp/1000.0
                return water_temp
            else:
                return False


relay = W1Relay("29-00000017b145")
status_int = relay.read_status_int()
if status_int == 0xff:
        print "All relays are off"
        print "Switching Relay 0 ON"
        relay.on(0)
elif status_int == 0xfe:
        print "Relay 0 is on"
        print "Switching Relay 0 OFF"
        relay.off(0)

thermometer = W1Thermometer("28-041470c98eff")
print thermometer.read_temp()