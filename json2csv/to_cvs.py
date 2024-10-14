import re
from anmeldungen import ANMELDUNGS_STATI, SUM_KEY, group_anmeldungen_by_status

DELIM = ";"


STUDI_FIELDS = ["Name", "Matrikelnr", "Studiengang", "FS"]

BasicInfoFields = ['anzahlPlaetze', 'bisherZugelassen', 'offeneBewerbungen', 'davonMitHoherPrio',
                     'davonMitNiedrigerPrio']



def studies_sums_field_names():
    sum_fields = [SUM_KEY]
    sum_fields.extend(ANMELDUNGS_STATI)
    return sum_fields


def studies_field_names(all_courses):
    field_names = STUDI_FIELDS.copy()
    field_names.extend(studies_sums_field_names())
    field_names.extend(all_courses)
    return field_names

def studies2csv(studies, all_courses):
    rows = [oneStudi2csv(s,a, STUDI_FIELDS, all_courses) for s, a in studies.items()]
    field_names = studies_field_names(all_courses)
    rows.insert(0, DELIM.join(field_names))
    return "\n".join(rows)

def oneStudi2csv(studi, anmeldungen, studi_fields, courses):
    # student info is the same in all anmeldungen, get it from first one
    eine_anmeldung = anmeldungen[0]
    values = [eine_anmeldung[fn] for fn in studi_fields]

    stati_sums = group_anmeldungen_by_status(anmeldungen)
    for one_sum in studies_sums_field_names():
        values.append(str(stati_sums.get(one_sum, "")))

    for course in courses:
        course_anmeldungen = [a for a in anmeldungen if a['Course'] == course]
        if len(course_anmeldungen) == 0:
            values.append("")
        else:
            if len(course_anmeldungen) != 1:
                if len(course_anmeldungen) == 2:
                    if course_anmeldungen[0] != course_anmeldungen[1]:
                        print("----zwei anmeldungen:")
                        print("\n".join([str(a) for a in course_anmeldungen]))
                        #raise ValueError("There should at most be one anmeldung per course at this point")
                else:
                    raise ValueError("There should at most be one anmeldung per course at this point")


            values.append(course_anmeldungen[0]["Status"])

    return DELIM.join(values)


def courses2csv(all_courses):
    sorted_courses = sorted(all_courses, key=lambda item: item['short_title'])
    field_names = ["Code", "Course", "Lehrperson"]
    field_names.extend(ANMELDUNGS_STATI)
    field_names.extend(["Summe"])
    field_names.extend(BasicInfoFields)
    rows = [oneCourse2csv(c, field_names) for c in sorted_courses]
    rows.insert(0, DELIM.join(field_names))
    return "\n".join(rows)+"\n"


def oneCourse2csv(course, fields):
    values = [get_course_number(course['short_title']), course['short_title']]              
    values.append(course['BasicInfo']['lehrpersonen'])
    for status in ANMELDUNGS_STATI:
        values.append(str(course['Stats'].get(status,"")))
    values.append(str(course['Stats']['Total']))
    for field_name in BasicInfoFields:
        values.append(str(course['BasicInfo'][field_name]))
    return DELIM.join(values)



def get_course_number(course_title):
    pattern = r"^B(\d+(\.\d+)?)"
    match = re.search(pattern, course_title)
    if match:
        return match.group(1)
    return ""
