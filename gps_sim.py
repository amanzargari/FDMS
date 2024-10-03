import random
import math

class GPSSimulator:
    """
    A class to simulate GPS readings for latitude, longitude, speed, and heading.
    Attributes:
        latitude (float): Current latitude of the simulator.
        longitude (float): Current longitude of the simulator.
        speed (float): Current speed of the simulator in km/h.
        heading (float): Current heading of the simulator in degrees.
        last_lat (float): Last recorded latitude.
        last_lon (float): Last recorded longitude.
    Methods:
        get_next_reading():
            Simulates the next GPS reading based on current speed and heading.
            Returns a tuple of (latitude, longitude, speed, heading).
        calculate_heading():
            Calculates the heading based on the change in latitude and longitude.
            Returns the heading in degrees.
    """
    def __init__(self, initial_lat=35.591556, initial_lon=53.399074, initial_speed=40):
        """
        Initializes the GPS simulator with initial latitude, longitude, and speed.

        Args:
            initial_lat (float): Initial latitude. Default is 35.591556.
            initial_lon (float): Initial longitude. Default is 53.399074.
            initial_speed (float): Initial speed in some unit. Default is 40.

        Attributes:
            latitude (float): Current latitude.
            longitude (float): Current longitude.
            speed (float): Current speed.
            heading (float): Current heading, initialized to 0.
            last_lat (float): Last recorded latitude.
            last_lon (float): Last recorded longitude.
        """
        self.latitude = initial_lat
        self.longitude = initial_lon
        self.speed = initial_speed  # User-defined initial speed
        self.heading = 0
        self.last_lat = initial_lat
        self.last_lon = initial_lon

    def get_next_reading(self):
        """
        Simulates the next GPS reading by updating the latitude, longitude, speed, and heading.
        This method performs the following steps:
        1. Updates the last known latitude and longitude.
        2. Simulates movement based on the current speed and heading.
        3. Updates the latitude and longitude with a scaled factor for more significant movement.
        4. Adjusts the speed slightly to simulate realistic driving conditions.
        5. Recalculates the heading.
        Returns:
            tuple: A tuple containing the updated latitude, longitude, speed, and heading.
        """
        self.last_lat, self.last_lon = self.latitude, self.longitude
        
        # Simulate movement based on speed and heading
        distance = self.speed / 3600  # Convert speed from km/h to km/s
        delta_lat = distance * math.cos(math.radians(self.heading))
        delta_lon = distance * math.sin(math.radians(self.heading))
        
        # Update latitude and longitude
        self.latitude += delta_lat * 0.1  # Scale factor for more significant movement
        self.longitude += delta_lon * 0.1  # Scale factor for more significant movement
        
        # Adjust speed slightly to simulate realistic driving conditions
        self.speed += random.uniform(-1, 1)  # Allow speed to fluctuate within ±5 km/h
        self.speed = max(0, min(self.speed, 150))  # Ensure speed stays within 0 to 60 km/h
        
        self.heading = self.calculate_heading()
        return self.latitude, self.longitude, self.speed, self.heading

    def calculate_heading(self):
        """
        Calculate the heading based on the current and last known GPS coordinates.

        This method computes the heading (direction) from the last known GPS 
        coordinates to the current GPS coordinates using the arctangent of the 
        differences in latitude and longitude. The result is converted from radians 
        to degrees and normalized to a value between 0 and 360 degrees.

        Returns:
            float: The heading in degrees, ranging from 0 to 360.
        """
        dy = self.latitude - self.last_lat
        dx = self.longitude - self.last_lon
        heading = math.degrees(math.atan2(dy, dx))
        return (heading + 360) % 360