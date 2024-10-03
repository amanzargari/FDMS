import datetime
import pytz
from convertdate import persian

class TimeDate:
    """
    TimeDate class provides methods to get current time, date, and datetime strings in a specified timezone.
    It also supports conversion to Solar Hijri calendar and Persian weekdays.
    Attributes:
        timezone (str): The timezone for datetime operations. Default is 'Asia/Tehran'.
        solar_hijri (bool): Flag to determine if Solar Hijri calendar should be used. Default is True.
    Methods:
        __init__(timezone='Asia/Tehran', solar_hijri=True):
            Initializes the TimeDate object with the specified timezone and calendar type.
        get_time_str() -> str:
            Returns the current time as a string in 'HH:MM:SS' format.
        get_date_str() -> str:
            Returns the current date as a string in 'YYYY-MM-DD' format.
        get_datetime_str() -> str:
            Returns the current datetime as a string in 'YYYY-MM-DD HH:MM:SS' format.
        get_hour() -> int:
            Returns the current hour as an integer.
        get_week_day() -> int:
            Returns the current day of the week as an integer. Converts to Solar Hijri weekday if solar_hijri is True.
        get_datetime() -> datetime.datetime:
            Returns the current datetime as a datetime object.
        gregorian_to_solar_weekday(gregorian_day: int) -> int:
            Converts a Gregorian weekday to a Solar Hijri weekday.
        persina_date() -> tuple[int, int, int]:
            Returns the current date as a tuple (year, month, day) in the Persian calendar.
        persian_week_day() -> str:
            Returns the current day of the week as a string in Persian.
    """
    def __init__(self, timezone='Asia/Tehran', solar_hijri=True):
        """
        Initializes the TimeDate object with the specified timezone and calendar type.

        Args:
            timezone (str): The timezone to be used. Default is 'Asia/Tehran'.
            solar_hijri (bool): If True, use the Solar Hijri calendar. Default is True.
        """
        self.timezone = timezone
        self.solar_hijri = solar_hijri
    
    def get_time_str(self) -> str:
        """
        Returns the current time as a string formatted as 'HH:MM:SS' in the specified timezone.

        Returns:
            str: The current time in 'HH:MM:SS' format.
        """
        time_now = datetime.datetime.now(pytz.timezone(self.timezone))
        return time_now.strftime('%H:%M:%S')
    
    def get_date_str(self) -> str:
        """
        Returns the current date as a string in the format 'YYYY-MM-DD'.

        The date is retrieved based on the timezone specified in the instance's
        `timezone` attribute.

        Returns:
            str: The current date formatted as 'YYYY-MM-DD'.
        """
        date_now = datetime.datetime.now(pytz.timezone(self.timezone))
        return date_now.strftime('%Y-%m-%d')
    
    def get_datetime_str(self) -> str:
        """
        Returns the current date and time as a formatted string.

        The date and time are retrieved based on the timezone specified
        in the instance's `timezone` attribute.

        Returns:
            str: The current date and time in the format 'YYYY-MM-DD HH:MM:SS'.
        """
        datetime_now = datetime.datetime.now(pytz.timezone(self.timezone))
        return datetime_now.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_hour(self) -> int:
        """
        Get the current hour in the specified timezone.

        Returns:
            int: The current hour (0-23) in the specified timezone.
        """
        return int(datetime.datetime.now(pytz.timezone(self.timezone)).strftime('%H'))
    
    def get_week_day(self) -> int:
        """
        Get the current day of the week.

        Returns the current day of the week as an integer. If the `solar_hijri` attribute is set to True,
        it converts the Gregorian day to the Solar Hijri weekday.

        Returns:
            int: The current day of the week, either in Gregorian or Solar Hijri format.
        """
        gregorian_day =  int(datetime.datetime.now(pytz.timezone(self.timezone)).strftime('%w'))
        if self.solar_hijri:
            return self.gregorian_to_solar_weekday(gregorian_day)
        else:
            return gregorian_day

    def get_datetime(self) -> datetime.datetime:
        """
        Get the current date and time in the specified timezone.

        Returns:
            datetime.datetime: The current date and time in the timezone specified by self.timezone.
        """
        return datetime.datetime.now(pytz.timezone(self.timezone))
    
    def gregorian_to_solar_weekday(self, gregorian_day:int) -> int:
        """
        Converts a given Gregorian day to the corresponding solar weekday.

        Args:
            gregorian_day (int): The day of the week in the Gregorian calendar (0 = Sunday, 1 = Monday, ..., 6 = Saturday).

        Returns:
            int: The corresponding day of the week in the solar calendar (0 = Sunday, 1 = Monday, ..., 6 = Saturday).
        """
        solar_weekday = (gregorian_day +1 ) % 7
        return solar_weekday
    
    def persina_date(self) -> tuple[int, int, int]:
        """
        Converts the current Gregorian date to the Persian date based on the specified timezone.

        Returns:
            tuple[int, int, int]: A tuple containing the Persian year, month, and day.
        """
        return persian.from_gregorian(int(datetime.datetime.now(pytz.timezone(self.timezone)).strftime('%Y')), int(datetime.datetime.now(pytz.timezone(self.timezone)).strftime('%m')), int(datetime.datetime.now(pytz.timezone(self.timezone)).strftime('%d')))
    
    def persian_week_day(self) -> str:
        """
        Returns the Persian name of the current weekday.

        The method uses the `get_week_day` method to determine the current weekday
        and maps it to the corresponding Persian weekday name.

        Returns:
            str: The Persian name of the current weekday.
        """
        persian_weekdays = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']
        return persian_weekdays[self.get_week_day()]
    
    def gregorian_week_day(self) -> str:
        """
        Returns the Gregorian name of the current weekday.

        The method uses the `get_week_day` method to determine the current weekday
        and maps it to the corresponding Gregorian weekday name.

        Returns:
            str: The Gregorian name of the current weekday.
        """
        gregorian_weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        return gregorian_weekdays[self.get_week_day()]