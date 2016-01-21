# global imports
import tornado.ioloop
import tornado.web
import tornado.httpserver
import sqlite3
import configparser
import time
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# read configuration file
config = configparser.SafeConfigParser()
config.read('config.ini')

_database_file = config.get('general', 'database_file')
_port = int(config.get('webservice', 'port'))
_min_temp = float(config.get('temperature', 'min'))
_max_temp = float(config.get('temperature', 'max'))
_invalid_value_temp = float(config.get('temperature', 'invalid_value'))
_min_humid = float(config.get('humidity', 'min'))
_max_humid = float(config.get('humidity', 'max'))
_invalid_value_humid = float(config.get('humidity', 'invalid_value'))
_timelag = float(config.get('general', 'timelag'))
_stamp_interval = float(config.get('plot', 'stamp_interval'))


class default_response(tornado.web.RequestHandler):
    def get(self):
        data = self.get_data()
        data = self.clean_data(data)
        current_date = time.strftime("%b %d %Y %H:%M:%S", time.gmtime(float(data[0, 0])))
        current_temp = data[0, 1]
        current_humid = data[0, 2]

        temp_style = self.get_style("current_temperature_", current_temp, _min_temp, _max_temp)
        humid_style = self.get_style("current_humidity_", current_humid, _min_humid, _max_humid)

        daily_mean_temp = np.round(np.mean(data[:, 1]), 2)
        daily_mean_humid = np.round(np.mean(data[:, 2]), 2)

        self.create_plot(data[:, 0], data[:, 1], data[:, 2])

        self.render("index.html", title="ClimatePi",
                    items=[[current_date, str(current_temp),
                            str(current_humid), temp_style,
                            humid_style, str(daily_mean_temp), str(daily_mean_humid)]])

    def get_data(self):
        start_time = time.time() - _timelag
        conn = sqlite3.connect(_database_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM climate WHERE date > %f ORDER BY date DESC" % (start_time))
        data = np.array(cursor.fetchall())
        conn.close()
        return data

    def clean_data(self, data):
        pos = np.logical_and((data[:, 1] - _invalid_value_temp) > 1e-10,
                             (data[:, 2] - _invalid_value_humid) > 1e-10)
        return data[pos]

    def get_style(self, prefix, v, minv, maxv):
        if v < minv:
            return prefix + "low"
        elif v > maxv:
            return prefix + "high"
        else:
            return prefix + "normal"

    def create_plot(self, times, temp, humid):
        start_time_full = times[-1] - (times[-1] % 3600)
        time_stamps = np.arange(start_time_full, times[0], _stamp_interval)
        time_stamps_labels = [time.strftime("%H:%M", time.gmtime(t)) for t in time_stamps]

        fig1 = plt.figure(1, figsize=(3.5, 3))

        ax_temp = fig1.add_axes((0.15, 0.6, 0.8, 0.37))
        ax_temp.spines['top'].set_visible(False)
        ax_temp.spines['right'].set_visible(False)
        ax_temp.get_xaxis().tick_bottom()
        ax_temp.get_yaxis().tick_left()
        ax_temp.set_ylabel('Temperature', fontsize=8)
        ax_temp.tick_params(axis='both', which='major', labelsize=7)
        ax_temp.tick_params(axis='both', which='minor', labelsize=6)
        ax_temp.set_xticks(time_stamps)
        ax_temp.set_xticklabels([])
        ax_temp.set_xlim((times[-1], times[0]))

        ax_humid = fig1.add_axes((0.15, 0.12, 0.8, 0.37))
        ax_humid.spines['top'].set_visible(False)
        ax_humid.spines['right'].set_visible(False)
        ax_humid.get_xaxis().tick_bottom()
        ax_humid.get_yaxis().tick_left()
        ax_humid.set_xlabel('Time', fontsize=8)
        ax_humid.set_ylabel('Rel. humidity', fontsize=8)
        ax_humid.tick_params(axis='both', which='major', labelsize=7)
        ax_humid.tick_params(axis='both', which='minor', labelsize=6)
        ax_humid.set_xticks(time_stamps)
        ax_humid.set_xticklabels(time_stamps_labels)
        ax_humid.set_xlim((times[-1], times[0]))

        ax_temp.plot(times, temp, marker='.', markersize=0.5, color='k')
        ax_temp.plot([times[-1], times[0]], [_min_temp, _min_temp], color='#3385ff')
        ax_temp.plot([times[-1], times[0]], [_max_temp, _max_temp], color='#ff3333')
        ax_humid.plot(times, humid, marker='.', markersize=0.5, color='k')
        ax_humid.plot([times[-1], times[0]], [_min_humid, _min_humid], color='#3385ff')
        ax_humid.plot([times[-1], times[0]], [_max_humid, _max_humid], color='#ff3333')
        fig1.savefig('static/images/climate.png', dpi=200)
        fig1.clf()


class dump_db(tornado.web.RequestHandler):
    def get(self):
        conn = sqlite3.connect(_database_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM climate")
        self.write(json.dumps(cursor.fetchall()))
        conn.close()
        self.finish()


class WebApplication(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", default_response),
            (r"/dumpdb/", dump_db)
        ]
        settings = {
            "debug": True,
            "template_path": "templates/",
            "static_path": "static/",
        }
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
    application = WebApplication()
    application.listen(_port)
    print '[info] Starting webservice on port %d.' % (_port)
    tornado.ioloop.IOLoop.instance().start()
