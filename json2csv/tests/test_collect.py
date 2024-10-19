import json
import os
import pytest
from json2csv import collect


def custom_read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data


@pytest.fixture
def course_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'test_data.json')
    course_data = custom_read_file(file_path)
    return course_data


DELIM = ";"
ANMELDUNGS_STATI = ['ZU', 'AN', 'KA', 'AB', 'ST']


def test_select_course(course_data):
    result = collect.select_course(course_data[1])
    assert result is not None
    assert result[1] == 'B21.2 - B23.2 WT2: Usability (Ü)'


def test_pseudonymize_name(course_data):
    names = [participant['Name'] for participant in course_data[1]['Teilnehmer']]
    pseudonym = [collect.pseudonymize_name(name) for name in names]
    assert collect.pseudonymize_name('John Doe') == pseudonym[0]
    assert collect.pseudonymize_name('Max Mustermann') == pseudonym[1]
    assert pseudonym[0] != pseudonym[1]


@pytest.mark.skip(reason="TODO")
def test_pseudonymize_matrikelnr():
    assert True

@pytest.mark.skip(reason="TODO")
def test_group_by_name():
    assert True

@pytest.mark.skip(reason="TODO")
def test_select_anmeldung_zulassung():
    assert True

@pytest.mark.skip(reason="TODO")
def test_add_stati_to_course():
    assert True

@pytest.mark.skip(reason="TODO")
def test_append_course():
    assert True

@pytest.mark.skip(reason="TODO")
def test_all_courses():
    assert True

@pytest.mark.skip(reason="TODO")
def test_json2studies():
    assert True

#--------------------------------------------------------------------


def test_short_title(course_data):
    result1 = collect.short_title(course_data[0])
    result2 = collect.short_title(course_data[1])
    assert result1 == ('B21.1 - B23.1 VCAT2 Visual Computing -  Aktuelle Themen 2: '
                       'Applikationsentwicklung unter iOS (Ü) - 2.Gruppe')
    assert result2 ==  'B21.2 - B23.2 WT2: Usability (Ü) - 1.Gruppe'


def test_get_course_number_with_valid_number(course_data):
    course_title = course_data[0]['BasicInfo']['vst_titel']
    result = collect.get_course_number(course_title)
    assert result == "21.1"


def test_get_course_number_with_no_valid_number():
    course_title = "English for International Media and Computing, M3Ts (GER B2.2)"
    result = collect.get_course_number(course_title)
    assert result == ""


def test_oneStudi2csv(course_data):
    fields = ["Name", "Matrikelnr", "Studiengang", "FS"]
    student = 'John Doe'
    anmeldungen = [
        {'Matrikelnr': '100001', 'Name': 'John Doe', 'Studiengang': 'IMI (B)', 'Status': 'AB', 'Prio': '1', 'Los': '9915927829841474', 'FS': '6', 'Zeit': '17.09.202416:24:27', 'Course': 'B21.1 - B23.1 VCAT2 Visual Computing -  Aktuelle Themen 2: Applikationsentwicklung unter iOS (Ü) - 2.Gruppe'},
    ]
    courses = [collect.short_title(c) for c in course_data]

    expected_output = "John Doe;100001;IMI (B);6;AB;"
    output = collect.oneStudi2csv(student, anmeldungen, fields, courses)
    assert output == expected_output


def test_studies2csv(course_data):
    studies = collect.json2studies(course_data)
    courses = [collect.short_title(c) for c in course_data]
    expected_output =  ('Name;Matrikelnr;Studiengang;FS;B21.1 - B23.1 VCAT2 Visual Computing -  '
                        'Aktuelle Themen 2: Applikationsentwicklung unter iOS (Ü) - 2.Gruppe;B21.2 - '
                        'B23.2 WT2: Usability (Ü) - 1.Gruppe\n'
                        ';100002;IMI (B);11;ZU;\n'
                        ';100003;IMI (B);10;ZU;\n'
                        ';100000;IMI (B);6;;AB\n'
                        ';100001;IMI (B);12;;AB')

    output = collect.studies2csv(studies, courses)
    output_lines = output.split('\n')
    expected_lines = expected_output.split('\n')

    assert len(output_lines) == len(expected_lines)

    for out_line, exp_line in zip(output_lines, expected_lines):
        assert exp_line in out_line


def test_courses2csv(course_data):
    studies = collect.json2studies(course_data)
    for course in course_data:
        studies = collect.append_course(studies, course)

    expected_output = ('Code;Course;Lehrperson;ZU;AN;KA;AB;ST;Summe;anzahlPlaetze;bisherZugelassen;offeneBewerbungen;davonMitHoherPrio;davonMitNiedrigerPrio\n'
                       '21.1;B21.1 - B23.1 VCAT2 Visual Computing -  Aktuelle Themen 2: '
                       'Applikationsentwicklung unter iOS (Ü) - 2.Gruppe;Jung;2;;;;;2;22; 20;5;1;4\n'
                       '21.2;B21.2 - B23.2 WT2: Usability (Ü) - 1.Gruppe;Hajinejad;;;;2;;2;22; '
                       '23;24;24;0\n')
    output = collect.courses2csv(course_data)
    assert output == expected_output


@pytest.mark.skip(reason="TODO")
def test_one_course2csv():
    assert True


@pytest.mark.skip(reason="TODO")
def test_read_file():
    assert True


@pytest.mark.skip(reason="TODO")
def test_write_output():
    assert True


@pytest.mark.skip(reason="TODO")
def test_run():
        assert True
