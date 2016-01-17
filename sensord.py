# global imports
import time
import configparser
import sqlite3

# local imports
import pigpio
import DHT22

config = configparser.SafeConfigParser()
config.read('config.ini')

database_file = config.get('general', 'database_file')
update_interval = float(config.get('sensor', 'update_interval'))
gpio_pin = int(config.get('sensor', 'gpio_pin'))

conn = sqlite3.connect(database_file)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS climate (date, temperature, humidity)")
conn.commit()

pi = pigpio.pi()
s = DHT22.sensor(pi, gpio_pin)

while(True):
    s.trigger()
    cursor.execute("INSERT INTO climate VALUES (%.0f, %.2f, %.2f)" % (time.time(), s.temperature(), s.humidity()))
    conn.commit()
    time.sleep(update_interval)
conn.close()
