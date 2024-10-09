import itertools

SUM_KEY = 'Sum'
ANMELDUNGS_STATI = ['ZU', 'AN', 'KA', 'AB', 'ST']


def group_anmeldungen_by_status(anmeldungen):
    by_status = lambda a : a['Status']
    anmeldungen_sorted = sorted(anmeldungen, key=by_status)
    grouped = itertools.groupby(anmeldungen_sorted, by_status)
    grouped = [(t[0], len(list(t[1]))) for t in grouped]
    grouped.reverse()
    grouped.insert(0,(SUM_KEY, len(anmeldungen)))
    grouped_dict = dict((y, x) for x, y in grouped)
    return grouped_dict
