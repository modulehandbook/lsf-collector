
import json
import re
import itertools
from collections import defaultdict, namedtuple, Counter
from anmeldungen import ANMELDUNGS_STATI
from to_cvs import courses2csv, studies2csv

#COURSE_NAME_RE = r'B21.\d - B23.\d(.*?)\(Ü\)'
COURSE_NAME_RE = r'(.*)'

def select_course(course):
    regex = COURSE_NAME_RE
    vst_titel = course['BasicInfo']['vst_titel']
    match = re.search(regex, vst_titel)
    return match

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
        newdict[studi] = sorted(anmeldungen,key=lambda item: item["Course"])
    return newdict

def short_title(course):
    c = course
    group = c['BasicInfo']['gruppe']
    pattern = re.compile(r'Gruppe:1.Zug,(\d.Gruppe)')
    match = re.match(pattern, group)
    group_short = match.group(1) if match else group
    return f"{c['BasicInfo']['vst_titel']} - {group_short}"







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

    # print(studies)
    # print(len(studies))
    name_numbers = [f"{k}, {len(a)}" for k, a in studies.items()]
    numbers = [len(a) for k, a in studies.items()]

    # titles = [short_title(c) for c in data]

    # print("\n".join(name_numbers))
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