import random
import math

class GPSSimulator:
    def __init__(self, initial_lat=35.591556, initial_lon=53.399074):
        self.latitude = initial_lat
        self.longitude = initial_lon
        self.speed = 0
        self.heading = 0
        self.last_lat = initial_lat
        self.last_lon = initial_lon

    def get_next_reading(self):
        self.last_lat, self.last_lon = self.latitude, self.longitude
        self.latitude += random.uniform(-0.0001, 0.0001)
        self.longitude += random.uniform(-0.0001, 0.0001)
        self.speed = random.uniform(0, 60)  # Speed in km/h
        self.heading = self.calculate_heading()
        return self.latitude, self.longitude, self.speed, self.heading

    def calculate_heading(self):
        dy = self.latitude - self.last_lat
        dx = self.longitude - self.last_lon
        heading = math.degrees(math.atan2(dy, dx))
        return (heading + 360) % 360