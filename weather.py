import requests
import config

class Weather:
    def __init__(self) -> None:
        self.wr = None
    
    def update(self, lat:float, lon:float) -> dict:
        r = requests.get(config.OpenWeatherMap_API_URL.format(lat=lat, lon=lon))
        self.wr = r.json()
        return self.wr
    
    def get_weather_id(self) -> int:
        return self.wr['weather'][0]['id']
    
    def get_weather_main(self) -> str:
        return self.wr['weather'][0]['main']
    
    def get_temp(self) -> float:
        return self.wr['main']['temp']
    
    def get_humidity(self) -> int:
        return self.wt['main']['humidity']
    
    def get_city_country(self) -> tuple[str, str]:
        return self.wr['name'], self.wr['sys']['country']
    
    def weather_id_to_condition_number(self, id:int) -> int:
        
        if id in config.inclement :
            return 2
        
        elif id in config.rainy:
            return 1
        
        elif id in config.normal:
            return 0
        
        else:
            return -1