import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import csv
from io import StringIO
from json2csv import collect, to_cvs

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


def test_pseudonymize_matrikelnr(course_data):
    names = [participant['Name'] for participant in course_data[1]['Teilnehmer']]
    pseudonymous_number = [collect.pseudonymize_matrikelnr(name) for name in names]
    assert collect.pseudonymize_matrikelnr('John Doe') == pseudonymous_number[0]
    assert collect.pseudonymize_matrikelnr('Max Mustermann') == pseudonymous_number[1]
    assert pseudonymous_number[0] != pseudonymous_number[1]


def test_group_by_name(course_data):
    participants = [participant for course in course_data for participant in course.get('Teilnehmer', [])]
    grouped_result = collect.group_by_name(participants)
    assert len(grouped_result) > 0
    for name, group in grouped_result:
        assert all(item['Name'] == name for item in group)
    total_count = sum(len(group) for _, group in grouped_result)
    assert total_count == len(participants)


def test_select_anmeldung_zulassung(course_data):
    tn_liste_for_one_name = course_data[0]['Teilnehmer']
    selected1 = collect.select_anmeldung_zulassung(tn_liste_for_one_name)
    assert selected1['Status'] == 'ZU'
    tn_liste_for_another_name = course_data[1]['Teilnehmer']
    selected2 = collect.select_anmeldung_zulassung(tn_liste_for_another_name)
    assert selected2['Status'] == 'AB'
    try:
        tn_liste_no_priority = [{'Status': 'XX'}, {'Status': 'YY'}]
        collect.select_anmeldung_zulassung(tn_liste_no_priority)
    except Exception as e:
        assert str(e) == "No matching status found"


def test_add_stati_to_course(course_data):
    course1 = course_data[0]
    selected_tn_stati1 = [(tn['Name'], tn) for tn in course1['Teilnehmer']]
    collect.add_stati_to_course(course1, selected_tn_stati1)
    expected_stats1 = {
        'ZU': 2,
        'Total': 2
    }
    assert course1['Stats'] == expected_stats1

    course2 = course_data[1]
    selected_tn_stati2 = [(tn['Name'], tn) for tn in course2['Teilnehmer']]
    collect.add_stati_to_course(course2, selected_tn_stati2)
    expected_stats2 = {
        'AB': 3,
        'Total': 3
    }
    assert course2['Stats'] == expected_stats2


def test_append_course(course_data):
    studies = collect.defaultdict(list)
    for course in course_data:
        collect.append_course(studies, course)
    expected_studies = {
        'Jane Doe': [{'Matrikelnr': '100002','Name': 'Jane Doe','Studiengang': 'IMI (B)','Status': 'ZU','Prio': '2','Los': '3435444759527443','FS': '11','Zeit': '15.09.202418:02:43','Course': 'B21.1 - B23.1 VCAT2 Visual Computing -  Aktuelle Themen 2: ''Applikationsentwicklung unter iOS (Ü) - 2.Gruppe'}],
        'Noah Clark': [{'Matrikelnr': '100003','Name': 'Noah Clark','Studiengang': 'IMI (B)','Status': 'ZU','Prio': '2','Los': '8266970658560711','FS': '10','Zeit': '26.09.202410:58:39','Course': 'B21.1 - B23.1 VCAT2 Visual Computing -  Aktuelle Themen 2: ''Applikationsentwicklung unter iOS (Ü) - 2.Gruppe'}]
    }
    for name in expected_studies:
        assert name in studies
        assert studies[name] == expected_studies[name]


def test_all_courses(course_data):
    result = collect.all_courses(course_data)
    expected_result = ['B21.1 - B23.1 VCAT2 Visual Computing -  Aktuelle Themen 2: ''Applikationsentwicklung unter iOS (Ü) - 2.Gruppe','B21.2 - B23.2 WT2: Usability (Ü) - 1.Gruppe']
    assert result == expected_result

def test_json2studies(course_data):
    result = collect.json2studies(course_data)
    expected_result = {
        'Jane Doe': [{'Course': 'B21.1 - B23.1 VCAT2 Visual Computing -  Aktuelle ''Themen 2: Applikationsentwicklung unter iOS (Ü) - ''2.Gruppe','FS': '11','Los': '3435444759527443','Matrikelnr': '100002','Name': 'Jane Doe','Prio': '2','Status': 'ZU','Studiengang': 'IMI (B)','Zeit': '15.09.202418:02:43'}],
        'John Doe': [{'Course': 'B21.2 - B23.2 WT2: Usability (Ü) - 1.Gruppe','FS': '6','Los': '9915927829841474','Matrikelnr': '100000','Name': 'John Doe','Prio': '1','Status': 'AB','Studiengang': 'IMI (B)','Zeit': '17.09.202416:24:27'}],
        'Max Mustermann': [{'Course': 'B21.2 - B23.2 WT2: Usability (Ü) - 1.Gruppe','FS': '12','Los': '8295249285091866','Matrikelnr': '100001','Name': 'Max Mustermann','Prio': '1','Status': 'AB','Studiengang': 'IMI (B)','Zeit': '11.09.202415:16:32'}],
        'Noah Clark': [{'Course': 'B21.1 - B23.1 VCAT2 Visual Computing -  Aktuelle ''Themen 2: Applikationsentwicklung unter iOS (Ü) - ''2.Gruppe','FS': '10','Los': '8266970658560711','Matrikelnr': '100003','Name': 'Noah Clark','Prio': '2','Status': 'ZU','Studiengang': 'IMI (B)','Zeit': '26.09.202410:58:39'}]}
    assert result == expected_result


def test_short_title(course_data):
    result1 = collect.short_title(course_data[0])
    result2 = collect.short_title(course_data[1])
    assert result1 == ('B21.1 - B23.1 VCAT2 Visual Computing -  Aktuelle Themen 2: '
                       'Applikationsentwicklung unter iOS (Ü) - 2.Gruppe')
    assert result2 ==  'B21.2 - B23.2 WT2: Usability (Ü) - 1.Gruppe'


def test_get_course_number_with_valid_number(course_data):
    course_title = course_data[0]['BasicInfo']['vst_titel']
    result = to_cvs.get_course_number(course_title)
    assert result == "21,1"


def test_get_course_number_with_no_valid_number():
    course_title = "English for International Media and Computing, M3Ts (GER B2.2)"
    result = to_cvs.get_course_number(course_title)
    assert result == ""


def test_oneStudi2csv(course_data):
    fields = ["Name", "Matrikelnr", "Studiengang", "FS"]
    student = 'John Doe'
    anmeldungen = [
        {'Matrikelnr': '100001', 'Name': 'John Doe', 'Studiengang': 'IMI (B)', 'Status': 'AB', 'Prio': '1', 'Los': '9915927829841474', 'FS': '6', 'Zeit': '17.09.202416:24:27', 'Course': 'B21.1 - B23.1 VCAT2 Visual Computing -  Aktuelle Themen 2: Applikationsentwicklung unter iOS (Ü) - 2.Gruppe'},
    ]
    courses = [collect.short_title(c) for c in course_data]

    expected_output = "John Doe;100001;IMI (B);6;1;;;;1;;AB;"
    output = to_cvs.oneStudi2csv(student, anmeldungen, fields, courses)
    assert output == expected_output


def test_studies2csv(course_data):
    studies = collect.json2studies(course_data)
    courses = [collect.short_title(c) for c in course_data]
    expected_output =  ('Name;Matrikelnr;Studiengang;FS;Sum;ZU;AN;KA;AB;ST;B21.1 - B23.1 VCAT2 Visual '
                        'Computing -  Aktuelle Themen 2: Applikationsentwicklung unter iOS (Ü) - '
                        '2.Gruppe;B21.2 - B23.2 WT2: Usability (Ü) - 1.Gruppe\n'
                        'Jane Doe;100002;IMI (B);11;1;1;;;;;ZU;\n'
                        'Noah Clark;100003;IMI (B);10;1;1;;;;;ZU;\n'
                        'John Doe;100000;IMI (B);6;1;;;;1;;;AB\n'
                        'Max Mustermann;100001;IMI (B);12;1;;;;1;;;AB')

    output = to_cvs.studies2csv(studies, courses)
    output_lines = output.split('\n')
    expected_lines = expected_output.split('\n')

    assert len(expected_lines) == len(output_lines)

    for out_line, exp_line in zip(expected_lines, output_lines):
        assert exp_line in out_line


def test_courses2csv(course_data):
    studies = collect.json2studies(course_data)
    for course in course_data:
        studies = collect.append_course(studies, course)

    expected_output = ('Code;Course;Lehrperson;ZU;AN;KA;AB;ST;Summe;anzahlPlaetze;bisherZugelassen;offeneBewerbungen;davonMitHoherPrio;davonMitNiedrigerPrio\n'
                       '21,1;B21.1 - B23.1 VCAT2 Visual Computing -  Aktuelle Themen 2: '
                       'Applikationsentwicklung unter iOS (Ü) - 2.Gruppe;Jung;2;;;;;2;22; 20;5;1;4\n'
                       '21,2;B21.2 - B23.2 WT2: Usability (Ü) - 1.Gruppe;Hajinejad;;;;2;;2;22; '
                       '23;24;24;0\n')
    output = collect.courses2csv(course_data)
    assert output == expected_output


def test_one_course2csv(course_data):
    studies = collect.json2studies(course_data)
    for course in course_data:
        studies = collect.append_course(studies, course)

    fields = ["Name", "Matrikelnr", "Studiengang", "FS"]
    course = course_data[0]
    expected_output = "21,1;B21.1 - B23.1 VCAT2 Visual Computing -  Aktuelle Themen 2: Applikationsentwicklung unter iOS (Ü) - 2.Gruppe;Jung;2;;;;;2;22; 20;5;1;4"
    output = to_cvs.oneCourse2csv(course, fields)
    assert expected_output == output


# for test_run_courselist() & test_run_courselist()
class Args:
    def __init__(self, filename, course_list, output):
        self.filename = filename
        self.courselist = course_list
        self.output = output


# for test_run_courselist() & test_run_courselist()
def read_csv_to_string(file_path):
    output = StringIO()
    with open(file_path, mode='r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            output.write(';'.join(row) + '\n')
    return output.getvalue()


def test_run_courselist():
    args = Args(
        filename="json2csv/tests/test_data.json",
        course_list="true",
        output="json2csv/tests/runTest.csv"
    )
    expected_output = ('Code;Course;Lehrperson;ZU;AN;KA;AB;ST;Summe;anzahlPlaetze;bisherZugelassen;offeneBewerbungen;davonMitHoherPrio;davonMitNiedrigerPrio\n'
                       '21,1;B21.1 - B23.1 VCAT2 Visual Computing -  Aktuelle Themen 2: Applikationsentwicklung unter iOS (Ü) - 2.Gruppe;Jung;2;;;;;2;22; 20;5;1;4\n'
                       '21,2;B21.2 - B23.2 WT2: Usability (Ü) - 1.Gruppe;Hajinejad;;;;2;;2;22; 23;24;24;0\n'
                       '\n')
    collect.run(args)

    output = read_csv_to_string("json2csv/tests/runTest.csv")
    assert expected_output == output


def test_run_without_courselist():
    args = Args(
        filename="json2csv/tests/test_data.json",
        course_list=None,
        output="json2csv/tests/runTestWithoutCourselist.csv"
    )
    expected_output = ('Name;Matrikelnr;Studiengang;FS;Sum;ZU;AN;KA;AB;ST;B21.1 - B23.1 VCAT2 Visual Computing -  Aktuelle Themen 2: Applikationsentwicklung unter iOS (Ü) - 2.Gruppe;B21.2 - B23.2 WT2: Usability (Ü) - 1.Gruppe\n'
                       'Jane Doe;100002;IMI (B);11;1;1;;;;;ZU;\n'
                       'Noah Clark;100003;IMI (B);10;1;1;;;;;ZU;\n'
                       'John Doe;100000;IMI (B);6;1;;;;1;;;AB\n'
                       'Max Mustermann;100001;IMI (B);12;1;;;;1;;;AB\n')
    collect.run(args)

    output = read_csv_to_string("json2csv/tests/runTestWithoutCourselist.csv")
    assert expected_output == output
