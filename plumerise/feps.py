"""plumerise.feps
"""

__author__      = "Joel Dubowy"

import csv
import logging
import math
import os
import subprocess
import tempfile

from . import compute_plumerise_hour


class FEPSPlumeRise(object):
    """FEPS Plumerise Module

    FEPSPlumeRise was copied from BlueSky Framework, and subsequently modified
    TODO: acknowledge original authors (STI?)
    """

    # required executables
    FEPS_WEATHER_BINARY = 'feps_weather'
    FEPS_PLUMERISE_BINARY = 'feps_plumerise'

    # How to model plume top.  Choices are:
    #     Briggs -- use the Briggs equation for plume top
    #     FEPS -- use the simplistic FEPS equation for plume top (2 * plume_bot)
    #     auto -- use the Briggs equation unless the result would be smaller than
    #             the plume bottom, in which case use the FEPS equation
    PLUME_TOP_BEHAVIOR = 'auto'


    def __init__(self, **config):
        self._config = config

    def config(self, key):
        return self._config.get(key.lower, getattr(self, key))

    def compute(self, timeprofile, consumption, fire_location_info,
            working_dir=None):
        working_dir = working_dir or tempfile.mkdtemp()
        plume_file = self._get_plume_file(timeprofile, consumption,
            fire_location_info, working_dir)

        return self._read_plumerise(plume_file, sorted(timeprofile.keys()))


    def _get_plume_file(self, timeprofile, consumption, fire_location_info,
            working_dir):
        timeprofile_file = os.path.join(working_dir, "profile.txt")
        consumption_file = os.path.join(working_dir, "cons.txt")
        plume_file = os.path.join(working_dir, "plume.txt")

        diurnal_file = self._get_diurnal_file(fire_location_info,
            working_dir)

        # TODO: This is rather hackish... is there a better way?
        self._write_profile(timeprofile, timeprofile_file)
        self._write_consumption(consumption, fire_location_info, consumption_file)

        plumerise_args = [
            self.config("FEPS_PLUMERISE_BINARY"),
            "-w", diurnal_file,
            "-p", timeprofile_file,
            "-c", consumption_file,
            "-a", str(fire_location_info["area"]),
            "-o", plume_file
        ]
        # TODO: log output?
        subprocess.check_output(plumerise_args)

        return plume_file

    def _get_diurnal_file(self, fire_location_info, working_dir):
        self._fill_fire_location_info(fire_location_info)

        weather_file = os.path.join(working_dir, "weather.txt")
        diurnal_file = os.path.join(working_dir, "diurnal.txt")

        f = open(weather_file, 'w')
        f.write("sunsetTime=%d\n" % fire_location_info['sunset_hour'])  # Time of sun set
        f.write("middayTime=%d\n" % fire_location_info['max_temp_hour'])  # Time of max temp
        f.write("predawnTime=%d\n" % fire_location_info['min_temp_hour'])   # Time of min temp
        f.write("minHumid=%f\n" % fire_location_info['min_humid'])  # Min humid
        f.write("maxHumid=%f\n" % fire_location_info['max_humid'])  # Max humid
        f.write("minTemp=%f\n" % fire_location_info['min_temp'])  # Min temp
        f.write("maxTemp=%f\n" % fire_location_info['max_temp'])  # Max temp
        f.write("minWindAtFlame=%f\n" % fire_location_info['min_wind']) # Min wind at flame height
        f.write("maxWindAtFlame=%f\n" % fire_location_info['max_wind']) # Max wind at flame height
        f.write("minWindAloft=%f\n" % fire_location_info['min_wind_aloft']) # Min transport wind aloft
        f.write("maxWindAloft=%f\n" % fire_location_info['max_wind_aloft']) # Max transport wind aloft
        f.close()

        weather_args = [
            self.config("FEPS_WEATHER_BINARY"),
            "-w", weather_file,
            "-o", diurnal_file
        ]
        # TODO: log output?
        subprocess.check_output(weather_args)

        return diurnal_file

    FIRE_LOCATION_INFO_DEFAULTS = {
        "min_wind": 6,
        "max_wind": 6,
        "min_wind_aloft": 6,
        "max_wind_aloft": 6,
        "min_humid": 40,
        "max_humid": 80,
        "min_temp": 13,
        "max_temp": 30,
        "min_temp_hour": 4,
        "max_temp_hour": 14,
        "snow_month": 5,
        "rain_days": 8,
        "sunrise_hour": 6,
        "sunset_hour": 18,
        # TODO: what is good default for 'moisture_duff'? I looked at one
        #   day (2015-08-05), and all listings has either 150.0 or 40.0
        "moisture_duff": 100.0
    }
    def _fill_fire_location_info(self, fire_location_info):
        for k, v in list(self.FIRE_LOCATION_INFO_DEFAULTS.items()):
            if fire_location_info.get(k) is None:
                fire_location_info[k] = v

    def _write_consumption(self, consumption, fire_location_info, filename):
        f = open(filename, 'w')
        f.write("cons_flm=%f\n" % consumption["flaming"])
        f.write("cons_sts=%f\n" % consumption["smoldering"])
        f.write("cons_lts=%f\n" % consumption["residual"])
        # TODO: what to do if duff consumption isn't defined? is 0.0 appropriate?
        f.write("cons_duff=%f\n" % consumption.get("duff", 0.0))
        f.write("moist_duff=%f\n" % fire_location_info['moisture_duff'])
        f.close()

    def _write_profile(self, timeprofile, timeprofile_file):
        with open(timeprofile_file, 'w') as f:
            f.write("hour, area_fract, flame, smolder, residual\n")
            hour = 0
            for dt in sorted(timeprofile.keys()):
                f.write("%d, %f, %f, %f, %f\n" % (
                    # TODO: should hour written to file reflect actual
                    #  number of hours since first time (which would be
                    #  different than 'hour' if timestep isn't one hour) ?
                    hour,
                    timeprofile[dt]["area_fraction"],
                    timeprofile[dt]["flaming"],
                    timeprofile[dt]["smoldering"],
                    timeprofile[dt]["residual"]))
                hour += 1

    def _read_plumerise(self, plume_file, sorted_timestamps):
        behavior = self.config("PLUME_TOP_BEHAVIOR").lower()
        plume_rise = {
            "hours": {}
        }

        hour = 0
        with open(plume_file, 'r') as f:
            for row in csv.DictReader(f, skipinitialspace=True):
                heat = float(row["heat"])

                smoldering_fraction = float(row["smold_frac"])
                plume_bottom_meters = float(row["plume_bot"])
                plume_top_meters = float(row["plume_top"])

                if heat == 0:
                    plume_top_meters = 0.0
                    plume_bottom_meters = 0.0

                if behavior == "briggs":
                    pass
                elif behavior == "feps":
                    plume_top_meters = plume_bottom_meters * 2
                elif behavior == "auto":
                    if plume_top_meters < plume_bottom_meters:
                        logging.debug("Adjusting plume_top for hour %d from Briggs to FEPS equation value", hour)
                        plume_top_meters = plume_bottom_meters * 2
                else:
                    raise Exception("Unknown value for PLUME_TOP_BEHAVIOR: %s", behavior)

                dt = sorted_timestamps[hour]
                plume_rise['hours'][dt] = compute_plumerise_hour(smoldering_fraction, plume_top_meters, plume_bottom_meters)
                hour += 1

        return plume_rise
