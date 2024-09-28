import os
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

OpenWeatherMap_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY')
OpenWeatherMap_API_URL = "https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric".format(api_key=OpenWeatherMap_API_KEY, lat='{lat}', lon='{lon}')