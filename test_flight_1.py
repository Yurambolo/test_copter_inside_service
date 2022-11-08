import time

from copter import MyCopter

connection_string = "/dev/ttyS2"


def main():
    copter = MyCopter()
    copter.connect(connection_string, baud=57600, heartbeat_timeout=120, timeout=120)
    # This test forces drone to take off, stand in place for 5 sec and land
    copter.arm_and_takeoff(1)
    time.sleep(5)
    copter.land()
    copter.disconnect()
