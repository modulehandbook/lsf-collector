

DELIM=";"

BasicInfoFields = ['anzahlPlaetze', 'bisherZugelassen', 'offeneBewerbungen', 'davonMitHoherPrio',
                     'davonMitNiedrigerPrio']


from anmeldungen import ANMELDUNGS_STATI

def studies2csv(studies, all_courses):
    fields = ["Name", "Matrikelnr", "Studiengang", "FS"]
    field_names = fields.copy()
    field_names.extend(all_courses)
    rows = [oneStudi2csv(s,a, fields, all_courses) for s, a in studies.items()]
    rows.insert(0, DELIM.join(field_names))
    return "\n".join(rows)

def oneStudi2csv(studi, anmeldungen, fields, courses):
    eine_anmeldung = anmeldungen[0]
    values = [eine_anmeldung[fn] for fn in fields]
    for course in courses:
        course_anmeldungen = [a for a in anmeldungen if a['Course'] == course]
        if len(course_anmeldungen) == 0:
            values.append("")
        else:
            if len(course_anmeldungen) != 1:
                raise ValueError("There should at most be one anmeldung per course at this point")
            assert len(course_anmeldungen) == 1
            values.append(course_anmeldungen[0]["Status"])

    return DELIM.join(values)


def courses2csv(all_courses):
    sorted_courses = sorted(all_courses, key=lambda item: item['short_title'])
    field_names = ["Course", "Lehrperson"]
    field_names.extend(ANMELDUNGS_STATI)
    field_names.extend(["Summe"])
    field_names.extend(BasicInfoFields)
    rows = [oneCourse2csv(c,field_names) for c in sorted_courses]
    rows.insert(0, DELIM.join(field_names))
    return "\n".join(rows)+"\n"

def oneCourse2csv(course, fields):
    values = [ course['short_title'] ]
    values.append(course['BasicInfo']['lehrpersonen'])
    for status in ANMELDUNGS_STATI:
        values.append(str(course['Stats'].get(status,"")))
    values.append(str(course['Stats']['Total']))
    for field_name in BasicInfoFields:
        values.append(str(course['BasicInfo'][field_name]))
    return DELIM.join(values)
