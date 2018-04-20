__author__      = "Joel Dubowy"

import copy
import os
import subprocess
import tempfile

#from numpy.testing import assert_approx_equal
from py.test import raises

from plumerise.feps import FEPSPlumeRise

class TestFEPSPlumeRise(object):


    def test_compute(self, monkeypatch):
        """Top level regression test of sorts for FEPSPlumeRise

        Note: the expected output data in this test is not known to be
        correct.  It's simply a snapshot taken after initial implementation
        of the FEPS model.  This test serves to ensure that future
        refactoring doesn't result in unexpected changes to output.

        Note: this test monkeypatches away the running of feps_weather and
        feps_plumerise.  Given that these two executables do the actual
        plumerise computation, this test basically just verifies that all
        input files are written correctly, and that the output plume file is
        read correctly.
        """
        monkeypatch.setattr(subprocess, "check_output", lambda *args: None)

        timeprofile = {
            "2014-05-29T22:00:00": {
                "area_fraction": 0.3333333333333333,
                "flaming": 0.3333333333333333,
                "residual": 0.3333333333333333,
                "smoldering": 0.3333333333333333
            },
            "2014-05-29T23:00:00": {
                "area_fraction": 0.3333333333333333,
                "flaming": 0.3333333333333333,
                "residual": 0.3333333333333333,
                "smoldering": 0.3333333333333333
            },
            "2014-05-30T00:00:00": {
                "area_fraction": 0.3333333333333333,
                "flaming": 0.3333333333333333,
                "residual": 0.3333333333333333,
                "smoldering": 0.3333333333333333
            }
        }
        consumption = {
            "flaming": 2165.6831964258654,
            "residual": 1761.0414186789003,
            "smoldering": 2091.3473506535884,
            "total": 6018.071965758354
        }
        location_info = {
            "area": 200,
            "ecoregion": "southern",
            "latitude": 47.4316976,
            "longitude": -121.3990506,
            "max_humid": 80,
            "max_temp": 30,
            "max_temp_hour": 14,
            "max_wind": 6,
            "max_wind_aloft": 6,
            "min_humid": 40,
            "min_temp": 13,
            "min_temp_hour": 4,
            "min_wind": 6,
            "min_wind_aloft": 6,
            "moisture_duff": 100.0,
            "rain_days": 8,
            "snow_month": 5,
            "sunrise_hour": 3,
            "sunset_hour": 19,
            "utc_offset": "-09:00"
        }

        expected_plumerise = {
            "2014-05-29T22:00:00": {
                "heights": [
                    614.072536,
                    1491.38933495,
                    2368.7061339,
                    3246.0229328500004,
                    4123.3397318,
                    5000.65653075,
                    5877.9733297,
                    6755.29012865,
                    7632.6069276,
                    8509.92372655,
                    9387.2405255,
                    10264.55732445,
                    11141.8741234,
                    12019.19092235,
                    12896.5077213,
                    13773.82452025,
                    14651.1413192,
                    15528.45811815,
                    16405.7749171,
                    17283.09171605,
                    18160.408515
                ],
                "emission_fractions": [
                    0.05, 0.05, 0.05, 0.05, 0.05,
                    0.05, 0.05, 0.05, 0.05, 0.05,
                    0.05, 0.05, 0.05, 0.05, 0.05,
                    0.05, 0.05, 0.05, 0.05, 0.05,
                ],
                "smolder_fraction": 0.05
            },
            "2014-05-29T23:00:00": {
                "heights": [
                    614.072536,
                    1391.61663015,
                    2169.1607243,
                    2946.70481845,
                    3724.2489126,
                    4501.79300675,
                    5279.337100899999,
                    6056.881195049999,
                    6834.4252891999995,
                    7611.96938335,
                    8389.5134775,
                    9167.057571649999,
                    9944.601665799999,
                    10722.145759949999,
                    11499.6898541,
                    12277.23394825,
                    13054.7780424,
                    13832.32213655,
                    14609.8662307,
                    15387.41032485,
                    16164.954419
                ],
                "emission_fractions": [
                    0.05, 0.05, 0.05, 0.05, 0.05,
                    0.05, 0.05, 0.05, 0.05, 0.05,
                    0.05, 0.05, 0.05, 0.05, 0.05,
                    0.05, 0.05, 0.05, 0.05, 0.05,
                ],
                "smolder_fraction": 0.493334
            },
            "2014-05-30T00:00:00": {
                "heights": [
                    614.072536,
                    1391.18509625,
                    2168.2976565,
                    2945.41021675,
                    3722.522777,
                    4499.63533725,
                    5276.747897499999,
                    6053.86045775,
                    6830.973018,
                    7608.085578249999,
                    8385.1981385,
                    9162.31069875,
                    9939.423259,
                    10716.535819249999,
                    11493.6483795,
                    12270.76093975,
                    13047.8735,
                    13824.98606025,
                    14602.098620499999,
                    15379.21118075,
                    16156.323741
                ],
                "emission_fractions": [
                    0.05, 0.05, 0.05, 0.05, 0.05,
                    0.05, 0.05, 0.05, 0.05, 0.05,
                    0.05, 0.05, 0.05, 0.05, 0.05,
                    0.05, 0.05, 0.05, 0.05, 0.05,
                ],
                "smolder_fraction": 0.493334
            }
        }
        expected_weather_file_contents = 'sunsetTime=19\nmiddayTime=14\npredawnTime=4\nminHumid=40.000000\nmaxHumid=80.000000\nminTemp=13.000000\nmaxTemp=30.000000\nminWindAtFlame=6.000000\nmaxWindAtFlame=6.000000\nminWindAloft=6.000000\nmaxWindAloft=6.000000\n'
        expected_timeprofile_file_contents = 'hour, area_fract, flame, smolder, residual\n0, 0.333333, 0.333333, 0.333333, 0.333333\n1, 0.333333, 0.333333, 0.333333, 0.333333\n2, 0.333333, 0.333333, 0.333333, 0.333333\n'
        expected_consumption_file_contents = 'cons_flm=10.828416\ncons_sts=10.456737\ncons_lts=8.805207\ncons_duff=0.000000\nmoist_duff=100.000000\n'

        working_dir = tempfile.mkdtemp()
        plume_file_content = 'hour, heat, smold_frac, plume_bot, plume_top\n0, 2082570545595.600342, 0.050000, 614.072536, 18160.408515\n1, 1110703180280.029053, 0.493334, 614.072536, 16164.954419\n2, 1110703180280.029053, 0.493334, 614.072536, 16156.323741\n'
        with open(os.path.join(working_dir, 'plume.txt'), 'w') as f:
            f.write(plume_file_content)
        # diurnal_file_contents = 'hour, temp, humid, wind_flame, modified_wind, stability, dif_temp_grad\n0, 15.270439, 74.657791, 6.000000, 5.364000, F, 0.025000\n1, 14.626840, 76.172140, 6.000000, 5.000000, F, 0.025000\n2, 14.165682, 77.257219, 6.000000, 5.000000, F, 0.025000\n3, 13.835248, 78.034711, 6.000000, 5.000000, F, 0.025000\n4, 13.000000, 80.000000, 6.000000, 5.000000, F, 0.025000\n5, 15.659386, 73.742621, 6.000000, 5.000000, B, -0.008000\n6, 18.253289, 67.639320, 6.000000, 5.000000, B, -0.008000\n7, 20.717838, 61.840380, 6.000000, 5.000000, B, -0.008000\n8, 22.992349, 56.488590, 6.000000, 5.000000, B, -0.008000\n9, 25.020815, 51.715729, 6.000000, 5.000000, B, -0.008000\n10, 26.753289, 47.639320, 6.000000, 5.000000, B, -0.008000\n11, 28.147111, 44.359739, 6.000000, 5.000000, B, -0.008000\n12, 29.167961, 41.957739, 6.000000, 5.000000, B, -0.008000\n13, 29.790702, 40.492466, 6.000000, 5.000000, B, -0.008000\n14, 30.000000, 40.000000, 6.000000, 5.000000, B, -0.008000\n15, 29.790702, 40.492466, 6.000000, 5.000000, B, -0.008000\n16, 29.167961, 41.957739, 6.000000, 5.000000, B, -0.008000\n17, 28.147111, 44.359739, 6.000000, 5.000000, B, -0.008000\n18, 26.753289, 47.639320, 6.000000, 5.000000, B, -0.008000\n19, 25.020815, 51.715729, 6.000000, 5.000000, B, -0.008000\n20, 21.613291, 59.733434, 6.000000, 5.000000, F, 0.025000\n21, 19.171692, 65.478371, 6.000000, 5.000000, F, 0.025000\n22, 17.422211, 69.594798, 6.000000, 5.000000, F, 0.025000\n23, 16.168653, 72.544347, 6.000000, 5.000000, F, 0.025000\n'
        # with open(os.path.join(working_dir, 'diurnal.txt'), 'w') as f:
        #     f.write(diurnal_file_contents)

        actual = FEPSPlumeRise().compute(timeprofile, consumption, location_info, working_dir)
        assert expected_plumerise == actual['hours']
        assert expected_weather_file_contents == open(os.path.join(working_dir, 'weather.txt'), 'r').read()
        assert expected_timeprofile_file_contents == open(os.path.join(working_dir, 'profile.txt'), 'r').read()
        assert expected_consumption_file_contents == open(os.path.join(working_dir, 'cons.txt'), 'r').read()
