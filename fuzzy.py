from simpful import FuzzySet, LinguisticVariable, FuzzySystem, AutoTriangle
import os
import config
import json

fuzzy_rules = os.path.join(config.ROOT_DIR, 'static', 'fuzzy rules', 'rules.json')

class FuzzyInference:
    def __init__(self) -> None:
        rules = self.load_rules_from_json_file()
        self.fuzzy_init(rules)
    
    def fuzzy_init(self, rules):
        week_day_ok= FuzzySet(points=[[0, 1], [3, 1], [4, 0]], term="weekday")
        week_day_danger= FuzzySet(points=[[3, 0], [4, 1], [6, 1]], term="weekend")
        lv_week_day = LinguisticVariable([week_day_ok, week_day_danger], universe_of_discourse=[0,6])

        day_hour_ok = FuzzySet(points=[[0, 1], [12,1], [13,0]], term="low")
        day_hour_medium = FuzzySet(points=[[13, 0], [14,1], [21,1], [22,0]], term="moderate")
        day_hour_danger = FuzzySet(points=[[12,0.],[13,1], [14,0], [21,0], [22,1], [24,1] ], term="high")
        lv_day_hour = LinguisticVariable([day_hour_ok, day_hour_medium, day_hour_danger], universe_of_discourse=[0,24])

        weather_ok = FuzzySet(points=[[1, 0], [2,1]], term="clear")
        weather_medium = FuzzySet(points=[[0, 0], [1,1], [2,0]], term="rainy")
        weather_danger = FuzzySet(points=[[0, 1], [1,0]], term="wet")
        lv_weather = LinguisticVariable([weather_ok, weather_medium, weather_danger], universe_of_discourse=[0,2])

        speed_ok = FuzzySet(points=[[65, 1], [70,0]], term="cautious")
        speed_medium = FuzzySet(points=[[65, 0], [75,1], [85,0]], term="elevated")
        speed_danger = FuzzySet(points=[[80, 0], [85,1], [220,1]], term="hazardous")
        lv_speed = LinguisticVariable([speed_ok, speed_medium, speed_danger], universe_of_discourse=[0,120])

        lv_sleep = AutoTriangle(2, terms=['awake', 'drowsy'], universe_of_discourse=[0, 1])

        result = AutoTriangle(5, terms=['very_low', 'low', 'medium', 'high', 'very_high'], universe_of_discourse=[0, 5])
        self.result = result

        fs = FuzzySystem(show_banner=False)
        fs.add_linguistic_variable("week_day", lv_week_day)
        fs.add_linguistic_variable("day_hour", lv_day_hour)
        fs.add_linguistic_variable("weather", lv_weather)
        fs.add_linguistic_variable("speed", lv_speed)
        fs.add_linguistic_variable("result", result)
        fs.add_linguistic_variable('sleep', lv_sleep)

        fs.add_rules(rules)

        self.fs = fs
    
    def load_rules_from_json_file(self):
        try:
            with open(fuzzy_rules, 'r') as f:
                rules_json = json.load(f)
        except IOError:
            print(f'Error: Failed to load rules from file {fuzzy_rules}')
            return []
        rules = []
        for rule_dict in rules_json:
            conditions = []
            for key, value in rule_dict.items():
                if key != 'result':
                    conditions.append(f'{key} IS {value}')
            results = f"THEN (result IS {rule_dict.get('result')})"
            rule = f'IF ({ ") AND (".join(conditions) }) {results}'
            rules.append(rule)
        
        return rules

    def __call__(self, hour=0, day=0, weather=0, speed=0, sleep=0):
        self.fs.set_variable("day_hour", hour)
        self.fs.set_variable("week_day", day)
        self.fs.set_variable("weather", weather)
        self.fs.set_variable("speed", speed)
        self.fs.set_variable("sleep", sleep)

        r = self.fs.inference()
        d = self.result.get_values(r['result'])
        max_value = max(d, key=d.get)
        
        return max_value        