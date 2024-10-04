import json

json_str = """
{"VstNr": "9194322", "BasicInfo": {"vstTyp": "Veranstaltungstyp: Übung", "vst_titel": "B21.2 - B23.2 WT2: Usability (Ü)", "gruppe": "Gruppe:1.Zug,1.Gruppe", "anzahlPlaetze": "22", "bisherZugelassen": " 23", "offeneBewerbungen": "0", "davonMitHoherPrio": "0", "davonMitNiedrigerPrio": "0" },
 "Teilnehmer": [
 {"Matrikelnr": "123457", "Name": "Jonas Nguyen", "Studiengang": "IMI (B)", "Status": "AB", "Prio": "1", "Los": "9915927829841474", "FS": "6", "Zeit": "17.09.202416:24:27" },
 {"Matrikelnr": "123456", "Name": "Habib Meier", "Studiengang": "IMI (B)", "Status": "AB", "Prio": "1", "Los": "8295249285091866", "FS": "12", "Zeit": "11.09.202415:16:32" },
 ] }


"""

import itertools
data = json.loads(json_str)
print(data)
teilnehmer = data["Teilnehmer"]
print(len(teilnehmer))
groups = itertools.groupby(teilnehmer, lambda item: item["Name"])
#grouped = list(groups)
grouped = groups
grouped = [(t[0], list(t[1])) for t in grouped]
print(grouped)
print(len(grouped))
