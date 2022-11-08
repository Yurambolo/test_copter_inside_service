import math
import time

from dronekit import connect, VehicleMode, LocationGlobal
from pymavlink import mavutil


class MyCopter:
    connection_string = None
    vehicle = None

    def __int__(self):
        pass

    def __del__(self):
        self.disconnect()

    def connect(self, connection_string, **kwargs):
        print("Connecting to vehicle on: %s" % (connection_string,))
        self.connection_string = connection_string
        self.vehicle = connect(connection_string, wait_ready=True, **kwargs)

    def disconnect(self):
        self.vehicle.close()

    def disarm(self):
        """
        Disarms vehicle.
        """

        print "Disarming motors"
        self.vehicle.armed = False
        while self.vehicle.armed:
            print "Waiting for disarming..."
            time.sleep(1)
        print "Disarmed!"

    def arm_and_takeoff(self, target_altitude):
        """
        Arms vehicle and fly to target_altitude.
        """

        print "Basic pre-arm checks"
        # Don't try to arm until autopilot is ready
        while not self.vehicle.is_armable:
            print " Waiting for vehicle to initialise..."
            time.sleep(1)

        print "Arming motors"
        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True

        # Confirm vehicle armed before attempting to take off
        while not self.vehicle.armed:
            print " Waiting for arming..."
            time.sleep(1)

        print "Taking off!"
        self.vehicle.simple_takeoff(target_altitude)  # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:

            print " Altitude: ", self.vehicle.location.global_relative_frame.alt
            # Break and return from function just below target altitude.
            if self.vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
                print "Reached target altitude"
                break
            time.sleep(1)

    def land(self):
        """
        Lands and disarms vehicle.
        """

        self.vehicle.mode = VehicleMode("LAND")
        while self.vehicle.armed:
            print " Altitude: ", self.vehicle.location.global_relative_frame.alt
            # Break and return from function just below target altitude.
            # if self.vehicle.location.global_relative_frame.alt <= 0:
            #     print "Landed"
            #     break
            time.sleep(1)

        print "Disarming motors"
        # while self.vehicle.armed:
        #     print "Waiting for disarming..."
        #     time.sleep(1)

    def return_to_launch(self):
        """
        Vehicle enters RTL mode and flies home.
        """

        home = self.vehicle.home_location  # type: LocationGlobal
        self.vehicle.mode = VehicleMode("RTL")
        while True:
            print " Position: ", self.vehicle.location.global_relative_frame
            # Break and return from function when home reached.
            distance = math.sqrt((self.vehicle.location.global_relative_frame.lat - home.lat) ** 2 + (
                    self.vehicle.location.global_relative_frame.lon - home.lon) ** 2)

            print " Distance to home: ", distance
            if distance <= 0.000005:
                print "Home reached"
                break
            time.sleep(1)

    def fly_to_coord(self, location, **kwargs):
        self.vehicle.simple_goto(location, **kwargs)

    def send_ned_velocity_global(self, velocity_x, velocity_y, velocity_z, duration):
        """
        Move vehicle in direction based on specified velocity vectors.
        """
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,  # time_boot_ms (not used)
            0, 0,  # target system, target component
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
            0b0000111111000111,  # type_mask (only speeds enabled)
            0, 0, 0,  # x, y, z positions (not used)
            velocity_x, velocity_y, velocity_z,  # x, y, z velocity in m/s
            0, 0, 0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

        # send command to vehicle on 1 Hz cycle
        for x in range(0, duration):
            self.vehicle.send_mavlink(msg)
            time.sleep(1)

    def send_ned_velocity_local(self, velocity_x, velocity_y, velocity_z, duration):
        """
        Move vehicle in direction based on specified velocity vectors.
        """
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,  # time_boot_ms (not used)
            0, 0,  # target system, target component
            mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,  # frame
            0b0000111111000111,  # type_mask (only speeds enabled)
            0, 0, 0,  # x, y, z positions (not used)
            velocity_x, velocity_y, velocity_z,  # x, y, z velocity in m/s
            0, 0, 0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

        # send command to vehicle on 1 Hz cycle
        for x in range(0, duration):
            self.vehicle.send_mavlink(msg)
            time.sleep(1)

    def print_metrics(self):
        print " GPS: %s" % self.vehicle.gps_0
        print " Battery: %s" % self.vehicle.battery
        print " Last Heartbeat: %s" % self.vehicle.last_heartbeat
        print " Is Armable?: %s" % self.vehicle.is_armable
        print " System status: %s" % self.vehicle.system_status.state
        print " Mode: %s" % self.vehicle.mode.name  # settable
