import requests
import config

class Weather:
    """
    A class to interact with the OpenWeatherMap API and retrieve weather information.
    Methods
    -------
    __init__() -> None
        Initializes the Weather object with no weather data.
    update(lat: float, lon: float) -> dict
        Updates the weather data for the given latitude and longitude.
    get_weather_id() -> int
        Returns the weather condition ID from the weather data.
    get_weather_main() -> str
        Returns the main weather condition description from the weather data.
    get_temp() -> float
        Returns the temperature from the weather data.
    get_humidity() -> int
        Returns the humidity percentage from the weather data.
    get_city_country() -> tuple[str, str]
        Returns the city name and country code from the weather data.
    weather_id_to_condition_number(id: int) -> int
        Converts a weather condition ID to a condition number based on predefined categories.
    """
    def __init__(self) -> None:
        self.wr = None
    
    def update(self, lat:float, lon:float) -> dict:
        """
        Updates the weather information for the given latitude and longitude.

        Args:
            lat (float): The latitude of the location.
            lon (float): The longitude of the location.

        Returns:
            dict: The weather information retrieved from the OpenWeatherMap API.
        """
        r = requests.get(config.OpenWeatherMap_API_URL.format(lat=lat, lon=lon))
        self.wr = r.json()
        return self.wr
    
    def get_weather_id(self) -> int:
        """
        Retrieves the weather ID from the weather data.

        Returns:
            int: The ID of the weather condition.
        """
        return self.wr['weather'][0]['id']
    
    def get_weather_main(self) -> str:
        """
        Retrieves the main weather condition.

        Returns:
            str: The main weather condition from the weather data.
        """
        return self.wr['weather'][0]['main']
    
    def get_temp(self) -> float:
        """
        Retrieves the temperature from the weather data.

        Returns:
            float: The temperature value from the weather data.
        """
        return self.wr['main']['temp']
    
    def get_humidity(self) -> int:
        """
        Retrieves the humidity value from the weather report.

        Returns:
            int: The humidity percentage.
        """
        return self.wr['main']['humidity']
    
    def get_city_country(self) -> tuple[str, str]:
        """
        Retrieves the city name and country code from the weather response.

        Returns:
            tuple[str, str]: A tuple containing the city name and the country code.
        """
        return self.wr['name'], self.wr['sys']['country']
    
    def weather_id_to_condition_number(self, id:int) -> int:
        """
        Converts a weather ID to a condition number.
        Args:
            id (int): The weather ID to be converted.
        Returns:
            int: The condition number corresponding to the weather ID.
                    - Returns 2 if the ID is in the inclement weather category.
                    - Returns 1 if the ID is in the rainy weather category.
                    - Returns 0 if the ID is in the normal weather category.
                    - Returns -1 if the ID does not match any known category.
        """
        
        if id in config.inclement :
            return 2
        
        elif id in config.rainy:
            return 1
        
        elif id in config.normal:
            return 0
        
        else:
            return -1