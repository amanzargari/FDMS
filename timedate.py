import datetime
import pytz
from convertdate import persian

class TimeDate:
    def __init__(self, timezone='Asia/Tehran', solar_hijri=True):
        self.timezone = timezone
        self.solar_hijri = solar_hijri
    
    def get_time_str(self) -> str:
        time_now = datetime.datetime.now(pytz.timezone(self.timezone))
        return time_now.strftime('%H:%M:%S')
    
    def get_date_str(self) -> str:
        date_now = datetime.datetime.now(pytz.timezone(self.timezone))
        return date_now.strftime('%Y-%m-%d')
    
    def get_datetime_str(self) -> str:
        datetime_now = datetime.datetime.now(pytz.timezone(self.timezone))
        return datetime_now.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_hour(self) -> int:
        return int(datetime.datetime.now(pytz.timezone(self.timezone)).strftime('%H'))
    
    def get_week_day(self) -> int:
        gregorian_day =  int(datetime.datetime.now(pytz.timezone(self.timezone)).strftime('%w'))
        if self.solar_hijri:
            return self.gregorian_to_solar_weekday(gregorian_day)
        else:
            return gregorian_day

    def get_datetime(self) -> datetime.datetime:
        return datetime.datetime.now(pytz.timezone(self.timezone))
    
    def gregorian_to_solar_weekday(self, gregorian_day:int) -> int:
        solar_weekday = (gregorian_day +1 ) % 7
        return solar_weekday
    
    def persina_date(self) -> tuple[int, int, int]:
        return persian.from_gregorian(int(datetime.datetime.now(pytz.timezone(self.timezone)).strftime('%Y')), int(datetime.datetime.now(pytz.timezone(self.timezone)).strftime('%m')), int(datetime.datetime.now(pytz.timezone(self.timezone)).strftime('%d')))
    
    def persian_week_day(self) -> str:
        persian_weekdays = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']
        return persian_weekdays[self.get_week_day()]