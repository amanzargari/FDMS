import random
import math

class GPSSimulator:
    def __init__(self, initial_lat=35.591556, initial_lon=53.399074, initial_speed=40):
        self.latitude = initial_lat
        self.longitude = initial_lon
        self.speed = initial_speed  # User-defined initial speed
        self.heading = 0
        self.last_lat = initial_lat
        self.last_lon = initial_lon

    def get_next_reading(self):
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
        dy = self.latitude - self.last_lat
        dx = self.longitude - self.last_lon
        heading = math.degrees(math.atan2(dy, dx))
        return (heading + 360) % 360