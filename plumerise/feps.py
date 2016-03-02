"""plumerise.feps
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import logging
import math

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

    def compute(self, timeprofile, consumption, moisture_duff, fire_area):
        plume_file = self._get_plume_file(timeprofile, consumption,
            moisture_duff, fire_area)

        heat, plume_rise = self._read_plumerise(plume_file, sorted(timeprofile.keys()))

        return {
            'heat': heat,
            'plume_rise': plume_rise
        }

    def _get_plume_file(self, timeprofile, consumption, moisture_duff):
        FEPS_PLUMERISE = self.config("FEPS_PLUMERISE_BINARY")
        if "extra:plume_file" in fireLoc["metadata"]:
            plume_file = fireLoc["metadata"]["extra:plume_file"]
        else:
            timeprofile_file = context.full_path("profile.txt")
            consumption_file = context.full_path("cons.txt")
            plume_file = context.full_path("plume.txt")
            context.archive_file(timeprofile_file)
            context.archive_file(plume_file)

            diurnal_file = self.get_diurnal_file(context, fireLoc)

            # TODO: This is rather hackish... is there a better way?
            self._write_profile(timeprofile, timeprofile_file)
            self._write_consumption(consumption, consumption_file)

            context.execute(FEPS_PLUMERISE,
                            "-w", diurnal_file,
                            "-p", timeprofile_file,
                            "-c", consumption_file,
                            "-a", str(fireLoc["area"]),
                            "-o", plume_file)
            fireLoc["metadata"]["extra:plume_file"] = plume_file
        return plume_file

    def get_diurnal_file(self, context, fireLoc):
        FEPS_WEATHER = self.config("FEPS_WEATHER_BINARY")
        if "extra:diurnal_file" in fireLoc["metadata"]:
            diurnalFile = fireLoc["metadata"]["extra:diurnal_file"]
        else:
            weatherFile = context.full_path("weather.txt")
            diurnalFile = context.full_path("diurnal.txt")
            context.archive_file(weatherFile)
            context.archive_file(diurnalFile)
            f = open(weatherFile, 'w')
            f.write("sunsetTime=%d\n" % fireLoc.local_weather.sunset_hour)  # Time of sun set
            f.write("middayTime=%d\n" % fireLoc.local_weather.max_temp_hour)  # Time of max temp
            f.write("predawnTime=%d\n" % fireLoc.local_weather.min_temp_hour)   # Time of min temp
            f.write("minHumid=%f\n" % fireLoc.local_weather.min_humid)  # Min humid
            f.write("maxHumid=%f\n" % fireLoc.local_weather.max_humid)  # Max humid
            f.write("minTemp=%f\n" % fireLoc.local_weather.min_temp)  # Min temp
            f.write("maxTemp=%f\n" % fireLoc.local_weather.max_temp)  # Max temp
            f.write("minWindAtFlame=%f\n" % fireLoc.local_weather.min_wind) # Min wind at flame height
            f.write("maxWindAtFlame=%f\n" % fireLoc.local_weather.max_wind) # Max wind at flame height
            f.write("minWindAloft=%f\n" % fireLoc.local_weather.min_wind_aloft) # Min transport wind aloft
            f.write("maxWindAloft=%f\n" % fireLoc.local_weather.max_wind_aloft) # Max transport wind aloft
            f.close()
            context.execute(FEPS_WEATHER,
                            "-w", weatherFile,
                            "-o", diurnalFile)
            fireLoc["metadata"]["extra:diurnal_file"] = diurnalFile
        return diurnalFile

    def _write_consumption(self, consumption, moisture_duff, filename):
        f = open(filename, 'w')
        f.write("cons_flm=%f\n" % consumption["flaming"])
        f.write("cons_sts=%f\n" % consumption["smoldering"])
        f.write("cons_lts=%f\n" % consumption["residual"])
        f.write("cons_duff=%f\n" % consumption["duff"])
        f.write("moist_duff=%f\n" % moisture_duff)
        f.close()

    def _write_profile(self, timeprofile_file):
        with open(timeprofile_file, 'w') as f:
            f.write("hour, area_fract, flame, smolder, residual\n")
            hour = 0
            for dt in sorted(timeprofile.keys()):
                f.write("%d, %f, %f, %f, %f\n" % (
                    # TODO: should hour written to file reflect actual
                    #  number of hours since first time (which would be
                    #  different than 'hour' if timestep isn't one hour) ?
                    hour,
                    timeprofile[dt]["area_fract"],
                    timeprofile[dt]["flaming"],
                    timeprofile[dt]["smoldering"],
                    timeprofile[dt]["residual"]))
                hour += 1

    def _read_plumerise(self, plume_file, sorted_timestamps):
        behavior = self.config("PLUME_TOP_BEHAVIOR").lower()
        plume_rise = {
            "hours": {},
            "heat": {}
        }

        hour = 0
        with open(plume_file, 'r') as f:
            for row in csv.DictReader(f, skipinitialspace=True):
                # Save the heat (returned as emissions, not plume rise)
                heat.append(float(row["heat"]))

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
                        self.log.debug("Adjusting plume_top for hour %d from Briggs to FEPS equation value", hour)
                        plume_top_meters = plume_bottom_meters * 2
                else:
                    raise Exception("Unknown value for PLUME_TOP_BEHAVIOR: %s", behavior)

                dt = sorted_timestamps[hour]
                plume_rise['hours'][dt] = compute_plumerise_hour(smoldering_fraction, plume_top_meters, plume_bottom_meters)
                hour += 1

        return heat, plumeRise
