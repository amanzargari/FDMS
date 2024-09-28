import os
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

OpenWeatherMap_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY')
OpenWeatherMap_API_URL = "https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric".format(api_key=OpenWeatherMap_API_KEY, lat='{lat}', lon='{lon}')

inclement = [600, 601, 602, 611, 612, 613, 615, 616, 620, 621, 622, 511, 762]
        
rainy = [500, 501, 502, 503, 504, 511, 520, 521, 522, 531, 
         300, 301, 302, 310, 311, 312, 313, 314, 321, 
         200, 201, 202, 210, 211, 212, 221, 230, 231, 232]
        
normal = [801, 802, 803, 804, 800, 701, 711, 721, 731, 741, 751, 761, 762, 771, 781,]