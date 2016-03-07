__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

__version_info__ = (0,2,0)
__version__ = '.'.join([str(n) for n in __version_info__])


def compute_plumerise_hour(smoldering_fraction, plume_top_meters, plume_bottom_meters):
    plume_rise_hr = {
        'smolder_fraction': smoldering_fraction #,
        # 'plume_bottom_meters': plume_bottom_meters,
        # 'plume_top_meters': plume_top_meters
    }

    if plume_top_meters is not None and plume_bottom_meters is not None:
        plume_rise_hr['percentile_000'] = plume_bottom_meters
        plume_rise_hr['percentile_100'] = plume_top_meters
        interp_percentile = lambda p : (plume_bottom_meters + ((plume_top_meters - plume_bottom_meters) / 100.0) * p)
        for p in range(5, 100, 5):
            plume_rise_hr["percentile_%03d" % p] = interp_percentile(p)

    return plume_rise_hr