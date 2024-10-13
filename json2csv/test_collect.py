import pytest
from json2csv import collect

# Example data from 'tryout.py' to use in tests
course_data = {
    'VstNr': '9194322',
    'BasicInfo': {
        'vstTyp': 'Veranstaltungstyp: Übung',
        'vst_titel': 'B21.2 - B23.2 WT2: Usability (Ü)',
        'gruppe': 'Gruppe:1.Zug,1.Gruppe',
        'anzahlPlaetze': 22,
        'bisherZugelassen': 23,
        'offeneBewerbungen': 0,
        'davonMitHoherPrio': 0,
        'davonMitNiedrigerPrio': 0
    },
    'Teilnehmer': [
        {'Matrikelnr': '123457', 'Name': 'Jonas Nguyen', 'Studiengang': 'IMI (B)', 'Status': 'AB', 'Prio': '1', 'Los': '9915927829841474', 'FS': '6', 'Zeit': '17.09.202416:24:27' },
        {'Matrikelnr': '123456', 'Name': 'Habib Meier', 'Studiengang': 'IMI (B)', 'Status': 'AB', 'Prio': '1', 'Los': '8295249285091866', 'FS': '12', 'Zeit': '11.09.202415:16:32' },
    ]
}


def test_select_course():
    result = collect.select_course(course_data)
    assert result is not None
    assert result[1] == 'B21.2 - B23.2 WT2: Usability (Ü)'


def test_pseudonymize_name():
    assert False


def test_pseudonymize_matrikelnr():
    assert False


def test_group_by_name():
    assert False


def test_select_anmeldung_zulassung():
    assert False


def test_add_stati_to_course():
    assert False


def test_append_course():
    assert False


def test_all_courses():
    assert False


def test_json2studies():
    assert False


def test_short_title():
    assert False


def test_get_course_number():
    assert False


def test_one_studi2csv():
    assert False


def test_studies2csv():
    assert False


def test_courses2csv():
    assert False


def test_one_course2csv():
    assert False


def test_read_file():
    assert False


def test_write_output():
    assert False


def test_run():
        assert False
