# global imports
import time
import configparser

# local imports
import pigpio
import DHT22

config = configparser.SafeConfigParser()
config.read('config.ini')

data_file = config.get('general', 'data_file')
update_interval = float(config.get('sensor', 'update_interval'))
gpio_pin = int(config.get('sensor', 'gpio_pin'))

pi = pigpio.pi()
s = DHT22.sensor(pi, gpio_pin)

f = open('climate_data.csv', 'w')
while(True):
    s.trigger()
    f.write('%.0f, %.2f, %.2f\n' % (time.time(), s.temperature(), s.humidity()))
    f.flush()
    time.sleep(update_interval)
f.close()
