"""plumerise.sev
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import logging
import math

class SEVPlumeRise(object):
    """

    SEVPlumeRise was copied from BlueSky Framework, and subsequently modified
    TODO: acknowledge original authors (STI?)
    """


    def compute(self, local_met, fire_area, smolder_fraction=0.0):
        """
        args
         - local_met
        kwargs
         - smoldering_fraction -- smoldering fraction of consumption (?)
         - frp -- FRP value (in units of Watts)
        """
        self.log.info("Running SEV Plume Rise model")

        local_met_array = [e[1] for e in sort(local_met.items(), key=lambda e: e[0])] # TODO: test this
        plume_rise = {}
        plume_rise['hours'] = []

        # loop over ordered list of hourly met data
        for met_loc in local_met_array:
            if not met_loc.get('HGTS') or not met_loc.get('RELH') or not met_loc.get('TPOT'):
                continue
            hourly_data = {}
            hourly_data['pressure'] = met_loc.get('pressure') # mb or hPa
            hourly_data['height'] = met_loc.get('HGTS') # m
            hourly_data['relative_humidity'] = met_loc.get('RELH') # %
            hourly_data['potential_temperature'] = met_loc.get('TPOT') # Kelvin
            hourly_data['wind_speed'] = met_loc.get('WSPD') # m/s
            hourly_data['wind_direction'] = met_loc.get('WDIR') # degrees
            hourly_data['temperature'] = met_loc.get('TEMP') # Celsius
            hourly_data['press_vertical_v'] = met_loc.get('WWND') # mb/h
            hourly_data['temp_at_2m'] = met_loc.get('TO2M') # Kelvin
            hourly_data['rh_at_2m'] = met_loc.get('RH2M') # %
            hourly_data['accum_precip_3hr'] = met_loc.get('TPP3') # m
            hourly_data['accum_precip_6hr'] = met_loc.get('TPP6') # m
            # The met file may spell this variable one of two ways
            pbl = met_loc.get('HPBL') if met_loc.get('PBLH') is None else met_loc.get('PBLH')
            hourly_data['height_abl'] = pbl                      # m

            # Get
            # FRP approximated by averaging the max values here:
            # http://www.gmes-atmosphere.eu/d/services/gac/nrt/fire_radiative_power
            # TODO: If known by caller, let frp be passed in directly rather than set to
            #  4180.8 * fire_area; if passed in value is < 0, set to 0
            hourly_data['frp'] = 4180.8 * fire_area

            plume_height = self.cal_smoke_height(hourly_data)
            plume_top_meters = plume_height
            plume_bottom_meters = plume_height * float(self.config("PLUME_BOTTOM_OVER_TOP"))

            plume_rise_hr = {
                'smolder_fraction': smolder_fraction #,
                # 'plume_bottom_meters': plume_bottom_meters,
                # 'plume_top_meters': plume_top_meters
            }

            if plume_top_meters is not None and plume_bottom_meters is not None:
                plume_rise_hr['percentile_000'] = plume_bottom_meters
                plume_rise_hr['percentile_100'] = plume_top_meters
                interp_percentile = lambda p : (plume_bottom_meters + ((plume_top_meters - plume_bottom_meters) / 100.0) * p)
                for p in range(5, 100, 5):
                    plume_rise_hr["percentile_%03d" % p] = interp_percentile(p)

            plume_rise['hours'].append(plume_rise_hr)

        return plume_rise


    # The two methods below represent all of the science in this model.
    # This master method calculates the height of the top of a smoke plume.
    def cal_smoke_height(self, hourly_data):
        """ Calculate the smoke height. This is the where most of the science happens. """
        alpha = float(self.config("ALPHA"))    # <1, Portion (fraction) of the abl passed freely
        beta = float(self.config("BETA"))      # >0 m, the contribution of fire intensity
        ref_power = float(self.config("REF_POWER"))  # reference fire power, Pf0 in paper
        gamma = float(self.config("GAMMA"))    # <0.5, determines power law dependence on FRP
        delta = float(self.config("DELTA"))    # > or = 0, defines dependence on stability in the free troposphere (FT)
        ref_n = float(self.config("REF_N"))    # Watts, Brunt-Vaisala reference frequency, N0^2 in paper

        nft = self.calc_brunt_vaisala(hourly_data)

        smoke_height = (alpha * float(hourly_data["height_abl"])) \
                       + (beta * math.pow(hourly_data["frp"] / ref_power, gamma)) \
                       * math.exp(-1.0 * delta * ((nft * nft) / ref_n))
        return smoke_height

    def calc_brunt_vaisala(self, hourly_data):
        """ The Brunt-Vaisala Frequency """
        gravity = float(self.config("GRAVITY"))  # m/s^2, gravitational constant

        theta_0 = hourly_data['potential_temperature'][0]
        theta_1 = hourly_data['potential_temperature'][1]

        nft = math.sqrt((gravity * 2) / (theta_0 + theta_1) * abs(theta_1 - theta_0) /
                        (hourly_data['height'][1] - hourly_data['height'][0]))
        return nft
