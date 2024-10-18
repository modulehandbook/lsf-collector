import hashlib
import json
import re
import itertools
from collections import defaultdict, namedtuple, Counter
from faker import Faker


DELIM=";"
#COURSE_NAME_RE = r'B21.\d - B23.\d(.*?)\(Ü\)'
COURSE_NAME_RE = r'(.*)'
ANMELDUNGS_STATI = ['ZU', 'AN', 'KA', 'AB', 'ST']

name_map = {}
matrikelnr_map = {}
matrikelnr_counter = 100000

def select_course(course):
    regex = COURSE_NAME_RE
    vst_titel = course['BasicInfo']['vst_titel']
    match = re.search(regex, vst_titel)
    return match

fake = Faker()
def pseudonymize_name(name):
    if name not in name_map:
        pseudonym = fake.name()
        name_map[name] = pseudonym
    return name_map[name]

def pseudonymize_matrikelnr(name):
    global matrikelnr_counter
    if name not in matrikelnr_map:
        matrikelnr_map[name] = f"{matrikelnr_counter}"
        matrikelnr_counter += 1
    return matrikelnr_map[name]

def group_by_name(teilnehmer):
    tn_sorted = teilnehmer.sort(key= lambda item: item["Name"])
    grouped = itertools.groupby(teilnehmer, lambda item: item["Name"])
    grouped = [(t[0], list(t[1])) for t in grouped]
    return grouped

def select_anmeldung_zulassung(tn_liste_for_one_name):
    for status in ANMELDUNGS_STATI:
        for anmeldung in tn_liste_for_one_name:
            if anmeldung['Status'] == status:
                return anmeldung
    raise Exception.new

def add_stati_to_course(course, selected_tn_stati):
    c = Counter()
    for studi, anmeldung in selected_tn_stati:
        c[anmeldung['Status']] += 1
    stats = dict(c)
    stats['Total'] = c.total()
    course['Stats'] = stats

def append_course(studies, course):
    teilnehmer = course["Teilnehmer"]
    course_title = short_title(course)
    course['short_title'] = course_title
    grouped = group_by_name(teilnehmer)
    selected_tn_stati = [(t[0], select_anmeldung_zulassung(t[1])) for t in grouped]
    for studi_anmeldung in selected_tn_stati:
        studi_anmeldung[1]['Name'] = pseudonymize_name(studi_anmeldung[0])
        studi_anmeldung[1]['Matrikelnr'] = pseudonymize_matrikelnr(studi_anmeldung[0])
        studi_anmeldung[1]['Course'] = course_title
        studies[studi_anmeldung[0]].append(studi_anmeldung[1])
    add_stati_to_course(course, selected_tn_stati)
    # all_courses[course_title] = course['BasicInfo']
    return studies

CourseInfo = namedtuple('CourseInfo', 'name, an, ab, department, paygrade')


def all_courses(data):
    selected_courses = [c for c in data if select_course(c)]
    return sorted([short_title(c) for c in selected_courses])

def json2studies(data):
    data = [c for c in data if select_course(c)]
    studies = defaultdict(list)
    for c in data:
        append_course(studies, c)
    newdict = {}
    for studi, anmeldungen in studies.items():
        name = pseudonymize_name(studi)
        newdict[name] = sorted(anmeldungen,key=lambda item: item["Course"])
    return newdict

def short_title(course):
    c = course
    group = c['BasicInfo']['gruppe']
    pattern = re.compile(r'Gruppe:1.Zug,(\d.Gruppe)')
    match = re.match(pattern, group)
    group_short = match.group(1) if match else group
    return f"{c['BasicInfo']['vst_titel']} - {group_short}"

def get_course_number(course_title):
    pattern = r"^B(\d+(\.\d+)?)"
    match = re.search(pattern, course_title)
    if match:
        return match.group(1)
    return ""

def oneStudi2csv(studi, anmeldungen, fields, courses):
    eine_anmeldung = anmeldungen[0]
    values = [eine_anmeldung[fn] for fn in fields]
    for course in courses:
        course_anmeldungen = [a for a in anmeldungen if a['Course'] == course]
        if len(course_anmeldungen) == 0:
            values.append("")
        else:
            if len(course_anmeldungen) != 1:
                pass
            assert len(course_anmeldungen) == 1
            values.append(course_anmeldungen[0]["Status"])

    return DELIM.join(values)

def studies2csv(studies, all_courses):
    fields = ["Name", "Matrikelnr", "Studiengang", "FS"]
    field_names = fields.copy()
    field_names.extend(all_courses)
    rows = [oneStudi2csv(s,a, fields, all_courses) for s, a in studies.items()]
    rows.insert(0, DELIM.join(field_names))
    return "\n".join(rows)


BasicInfoFields = ['anzahlPlaetze', 'bisherZugelassen', 'offeneBewerbungen', 'davonMitHoherPrio',
                     'davonMitNiedrigerPrio']


def courses2csv(all_courses):
    sorted_courses = sorted(all_courses, key=lambda item: item['short_title'])
    field_names = ["Code", "Course", "Lehrperson"]
    field_names.extend(ANMELDUNGS_STATI)
    field_names.extend(["Summe"])
    field_names.extend(BasicInfoFields)
    rows = [oneCourse2csv(c,field_names) for c in sorted_courses]
    rows.insert(0, DELIM.join(field_names))
    return "\n".join(rows)+"\n"


def oneCourse2csv(course, fields):
    values = [get_course_number(course['short_title']), course['short_title'], course['BasicInfo']['lehrpersonen']]
    for status in ANMELDUNGS_STATI:
        values.append(str(course['Stats'].get(status,"")))
    values.append(str(course['Stats']['Total']))
    for field_name in BasicInfoFields:
        values.append(str(course['BasicInfo'][field_name]))
    return DELIM.join(values)

    pass
def read_file(filename):
    with open(filename) as fp:
        data = json.load(fp)
        return data

def write_output(args, rows):
    if (args.output is None):
        print(rows)
    else:
        with open(args.output, "w") as file:
            file.write(rows)
            file.write("\n")

def run(args):
    filename = args.filename
    data = read_file(filename)

    studies = json2studies(data)

    print(studies)
    print(len(studies))
    name_numbers = [f"{k}, {len(a)}" for k, a in studies.items()]
    numbers = [len(a) for k, a in studies.items()]

    # titles = [short_title(c) for c in data]

    print("\n".join(name_numbers))
    print(f"{len(studies)} Studis")
    print(f"{sum(numbers)} Einzelanmeldungen")


    #print(numbers)
    sorted_numbers = sorted(numbers, reverse=True)
    #print(sorted_numbers)
    grouped_numbers = itertools.groupby(sorted_numbers)
    grouped_numbers = [(n[0], len(list(n[1]))) for n in grouped_numbers]
    print(grouped_numbers)
    #grouped_numbers = [(n[0],list(n[1])) for n in grouped_numbers]
    #print(list(grouped_numbers))

    if args.courselist:
        rows = courses2csv(data)
    else:
        rows = studies2csv(studies, all_courses(data))

    #print(rows)
    #print("\n".join(rows))
    print("\n".join(all_courses(data)))
    write_output(args, rows)



    if __name__ == '__main__':
        run()