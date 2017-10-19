__author__      = "Joel Dubowy"

__version_info__ = (1,0,0)
__version__ = '.'.join([str(n) for n in __version_info__])


def compute_plumerise_hour(smoldering_fraction, plume_top_meters, plume_bottom_meters):
    plume_rise_hr = {
        'smolder_fraction': smoldering_fraction #,
        # 'plume_bottom_meters': plume_bottom_meters,
        # 'plume_top_meters': plume_top_meters
    }

    if plume_top_meters is not None and plume_bottom_meters is not None:
        # evenly distribute emissions among 20 vertical layers between
        # plume bottom and plume top
        spacing = (plume_top_meters - plume_bottom_meters) / 20
        plume_rise_hr['heights'] = [plume_bottom_meters + n * spacing
            for n in range(21)]
        plume_rise_hr['emission_fractions'] = [0.05] * 20

    return plume_rise_hr