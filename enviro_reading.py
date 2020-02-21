import time
import os
import sys
import json
from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError
from enviroplus import gas
from subprocess import PIPE, Popen
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus


class EnviroReading:
    def __init__(self, temp = True, pressure = True, humidity = True, light = True, oxidised = True, reduced = True, nh3 = True, pm1 = True, pm10 = True, pm25 = True):
        self.__variables = {
            "temp" : temp,
            "pressure" : pressure,
            "humidity" : humidity,
            "light" : light,
            "oxidised" : oxidised,
            "reduced" : reduced,
            "nh3" : nh3,
            "pm1" : pm1,
            "pm25" : pm25,
            "pm10" : pm10
        }

        # Pre-load sensor packages
        if (self.__variables['temp'] or self.__variables['pressure'] or self.__variables['humidity']):
            bus = SMBus(1)
            self.bme280 = BME280(i2c_dev=bus)
            # Take initial reading then allow time to get it to 
            self.init_temp_reading = self.bme280.get_temperature()
            self.init_pressure = self.bme280.get_pressure()
            self.init_humidity = self.bme280.get_humidity()
            time.sleep(1)
        if self.__variables['light']:
            self.ltr559 = LTR559()
        if (self.__variables['pm1'] or self.__variables['pm25'] or self.__variables['pm10']):
            self.pms5003 = PMS5003()
        if (self.__variables['oxidised'] or self.__variables['reduced'] or self.__variables['nh3']):
            self.gas_data = gas.read_all()

        # Define output
        self.output_dict = {
            'timestamp' : time.time(),
            'script_version' : '0.0.1'
        }

    def generate_output(self):
        if self.__variables['temp']: 
            self.output_dict['temp'] = {}
            self.output_dict['temp']['value'] = self.bme280.get_temperature()
            self.output_dict['temp']['unit'] = 'C'
        if self.__variables['pressure']:
            self.output_dict['pressure'] = {}
            self.output_dict['pressure']['value'] = self.bme280.get_pressure()
            self.output_dict['pressure']['unit'] = 'hPa'
        if self.__variables['humidity']:
            self.output_dict['humidity'] = {}
            self.output_dict['humidity']['value'] = self.bme280.get_humidity()
            self.output_dict['humidity']['unit'] = '%'
        if self.__variables['light']:
            proximity = ltr559.get_proximity()
            if proximity < 10:
                light_value = self.ltr559.get_lux()
            else:
                light_value = 1
            self.output_dict['light'] = {}
            self.output_dict['light']['value'] = light_value
            self.output_dict['light']['unit'] = 'Lux'
        if self.__variables['oxidised']:
            self.output_dict['oxidised'] = {}
            self.output_dict['oxidised']['value'] = self.gas_data.oxidising / 1000
            self.output_dict['oxidised']['unit'] = 'kO'
        if self.__variables['reduced']:
            self.output_dict['reduced'] = {}
            self.output_dict['reduced']['value'] = self.gas_data.reducing / 1000
            self.output_dict['reduced']['unit'] = 'kO'
        if self.__variables['nh3']:
            self.output_dict['nh3'] = {}
            self.output_dict['nh3']['value'] = self.gas_data.nh3 / 1000
            self.output_dict['nh3']['unit'] = 'kO'
        if self.__variables['pm1']:
            self.output_dict['pm1'] = {}
            self.output_dict['pm1']['value'] = float(self.pms5003.read().pm_ug_per_m3(1.0))
            self.output_dict['pm1']['unit'] = 'ug/m3'
        if self.__variables['pm25']:
            self.output_dict['pm25'] = {}
            self.output_dict['pm25']['value'] = float(self.pms5003.read().pm_ug_per_m3(2.5))
            self.output_dict['pm25']['unit'] = 'ug/m3'
        if self.__variables['pm10']:
            self.output_dict['pm10'] = {}
            self.output_dict['pm10']['value'] = float(self.pms5003.read().pm_ug_per_m3(10))
            self.output_dict['pm10']['unit'] = 'ug/m3'
        return self.output_dict

    def output_json(self):
        return json.dumps(self.generate_output())

# Testing
if False:
    x = EnviroReading()
    print(x.output_json())
