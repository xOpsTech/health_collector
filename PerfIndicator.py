from constatnts import *


class PerfIndicator(object):
    def __init__(self):
        self.id = None
        self.type = TYPE_PERFORMANCE
        self.red_threshold = None
        self.orange_threshold = None
        self.yellow_threshold = None
        self.blue_threshold = None
        self.green_threshold = None
        self.value = None
        self.health_value = None
        self.health = None
        self.importance = None
        self.is_boolean = False

    def calculate_health_value(self):
        if self.value < self.green_threshold:
            self.health_value = OK_VALUE
        elif self.green_threshold <= self.value < self.blue_threshold:
            self.health_value = GREEN_VALUE
        elif self.blue_threshold <= self.value < self.yellow_threshold:
            self.health_value = BLUE_VALUE
        elif self.yellow_threshold <= self.value < self.orange_threshold:
            self.health_value = YELLOW_VALUE
        elif self.orange_threshold <= self.value < self.red_threshold:
            self.health_value = ORANGE_VALUE
        else:
            self.health_value = RED_VALUE
