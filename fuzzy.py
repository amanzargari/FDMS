from simpful import FuzzySet, LinguisticVariable, FuzzySystem, AutoTriangle, SingletonsSet
import os
import config
import json

fuzzy_rules = os.path.join(config.ROOT_DIR, 'static', 'fuzzy rules', 'rules.json')

class FuzzyInference:
    """
    FuzzyInference class for performing fuzzy logic inference based on predefined rules and linguistic variables.
    Methods:
        __init__() -> None:
            Initializes the FuzzyInference system by loading rules from a JSON file and setting up the fuzzy logic system.
        fuzzy_init(rules):
            Initializes the fuzzy logic system with linguistic variables and rules.
            Parameters:
                rules (list): List of fuzzy logic rules.
        load_rules_from_json_file():
            Loads fuzzy logic rules from a JSON file.
            Returns:
                list: List of fuzzy logic rules in string format.
        __call__(hour=0, day=0, weather=0, speed=0, sleep=0):
            Performs fuzzy logic inference based on input variables.
            Parameters:
                hour (int): Hour of the day (default is 0).
                day (int): Day of the week (default is 0).
                weather (int): Weather condition (default is 0).
                speed (int): Speed of the vehicle (default is 0).
                sleep (int): Sleep condition (default is 0).
            Returns:
                str: The term with the highest membership value from the result of the inference.
    """
    def __init__(self) -> None:
        """
        Initializes the fuzzy logic system by loading rules from a JSON file and 
        initializing the fuzzy logic system with these rules.

        Args:
            None

        Returns:
            None
        """
        rules = self.load_rules_from_json_file()
        self.fuzzy_init(rules)
    
    def fuzzy_init(self, rules):
        """
        Initializes the fuzzy logic system with the provided rules and sets up the linguistic variables.
        Args:
            rules (list): A list of fuzzy logic rules to be added to the fuzzy system.
        Attributes:
            result (LinguisticVariable): The linguistic variable representing the result with five terms: 'very_low', 'low', 'medium', 'high', 'very_high'.
            fs (FuzzySystem): The fuzzy system instance containing all the linguistic variables and rules.
        Linguistic Variables:
            week_day (LinguisticVariable): Represents the day of the week with terms 'weekday' and 'weekend'.
            day_hour (LinguisticVariable): Represents the hour of the day with terms 'low', 'moderate', and 'high'.
            weather (LinguisticVariable): Represents the weather condition with terms 'normal', 'rainy', and 'inclement'.
            speed (LinguisticVariable): Represents the speed with terms 'cautious', 'elevated', and 'hazardous'.
            sleep (LinguisticVariable): Represents the sleep state with terms 'awake' and 'drowsy'.
        Example:
            rules = [
                "IF (week_day IS weekday) AND (day_hour IS low) THEN (result IS very_low)",
                "IF (weather IS inclement) OR (speed IS hazardous) THEN (result IS very_high)"
            ]
            fuzzy_init(rules)
        """
        week_day_ok= FuzzySet(points=[[0, 1], [3, 1], [4, 0]], term="weekday")
        week_day_danger= FuzzySet(points=[[3, 0], [4, 1], [6, 1]], term="weekend")
        lv_week_day = LinguisticVariable([week_day_ok, week_day_danger], universe_of_discourse=[0,6])

        day_hour_ok = FuzzySet(points=[[0, 1], [12,1], [13,0]], term="low")
        day_hour_medium = FuzzySet(points=[[13, 0], [14,1], [21,1], [22,0]], term="moderate")
        day_hour_danger = FuzzySet(points=[[12,0.],[13,1], [14,0], [21,0], [22,1] ], term="high")
        lv_day_hour = LinguisticVariable([day_hour_ok, day_hour_medium, day_hour_danger], universe_of_discourse=[0,24])

        weather_ok = SingletonsSet(pairs=[[0,1]], term="normal")
        weather_medium = SingletonsSet(pairs=[[1, 1]], term="rainy")
        weather_danger = SingletonsSet(pairs=[[2, 1]], term="inclement")
        lv_weather = LinguisticVariable([weather_ok, weather_medium, weather_danger], universe_of_discourse=[0, 2])

        speed_ok = FuzzySet(points=[[65, 1], [70,0]], term="cautious")
        speed_medium = FuzzySet(points=[[65, 0], [75,1], [85,0]], term="elevated")
        speed_danger = FuzzySet(points=[[80, 0], [85,1], [120,1]], term="hazardous")
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
        """
        Loads fuzzy logic rules from a JSON file and converts them into a list of human-readable strings.
        The JSON file should contain a list of dictionaries, where each dictionary represents a rule.
        Each dictionary should have keys representing conditions and a special key 'result' for the rule's outcome.
        Example of JSON structure:
        [
            {"condition1": "value1", "condition2": "value2", "result": "outcome1"},
            {"condition1": "value3", "condition2": "value4", "result": "outcome2"}
        ]
        Returns:
            list: A list of strings, where each string represents a fuzzy logic rule in the format:
                  "IF (condition1 IS value1) AND (condition2 IS value2) THEN (result IS outcome1)"
                  If the file cannot be read, an empty list is returned.
        """
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
        """
        Perform fuzzy logic inference based on the provided parameters.
        Parameters:
        hour (int): The hour of the day (default is 0).
        day (int): The day of the week (default is 0).
        weather (int): The weather condition (default is 0).
        speed (int): The speed of the vehicle (default is 0).
        sleep (int): The sleep level of the driver (default is 0).
        Returns:
        str: The result of the fuzzy logic inference with the highest value.
        """
        self.fs.set_variable("day_hour", hour)
        self.fs.set_variable("week_day", day)
        self.fs.set_variable("weather", weather)
        self.fs.set_variable("speed", speed)
        self.fs.set_variable("sleep", sleep)

        r = self.fs.inference()
        d = self.result.get_values(r['result'])
        max_value = max(d, key=d.get)
        
        return max_value        