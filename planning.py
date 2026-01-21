from z3 import *
from tabulate import tabulate


#on définit les types Week, Day, Hour, Nurse, Status
Week, (W1,W2,W3,W4) =  EnumSort('Week',('W1','W2','W3','W4'))
Day, (J1,J2,J3,J4,J5,We) = EnumSort('Day',('Monday','Tuesday','Wednesday','Thursday','Friday','We'))
Hour,(AM,PM)= EnumSort('Hour',('AM','PM'))
Nurse, (N1,N2,N3,N4) = EnumSort('Nurse',('N1','N2','N3','N4'))
Status, (Work,Rest)= EnumSort('Status',('Work','Rest'))

#on instancie des variables avec nos nouveaux types
jours_de_la_semaine=[J1,J2,J3,J4,J5,We]
jours_hors_we = [J1,J2,J3,J4,J5]
semaines = [W1,W2,W3,W4]
infirmieres = [N1,N2,N3,N4]
heures_de_la_journee=[AM,PM]

#on définit une fonction utilitaire qui permet d'afficher ou d'enregistrer les plannings de chacun
def print_planning(model_as_list, nurse: Nurse,save=False):
    week_converter = {W1: 0, W2: 1, W3: 2, W4: 3}
    day_converter = {J1: 1, J2: 2, J3: 3, J4: 4, J5: 5, We: 6}
    hour_converter = {AM: 0, PM: 2}

    else_value = 'R' if model_as_list[-1] == Rest else 'W'
    data = [
        ["Week 1", f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}",
         f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}"],
        ["Week 2", f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}",
         f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}"],
        ["Week 3", f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}",
         f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}"],
        ["Week 4", f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}",
         f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}"],
    ]
    for case in model_as_list[:-1]:
        if case[3] == nurse:
            week = week_converter[case[0]]
            day = day_converter[case[1]]
            hour = hour_converter[case[2]]
            value = 'R' if case[4] == Rest else 'W'
            data[week][day] = data[week][day][:hour] + value + data[week][day][hour + 1:]

    headers = ["Week", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "We"]
    print(f"Emploi du temps for Nurse {nurse}")
    content = tabulate(data, headers=headers, tablefmt="grid")
    print(content)
    if save:
        with open(f"planning_infirmiere_{nurse}.csv", 'w') as file:
            file.write(content)
            file.close()
#on définit une fonction utilitaire qui permet d'afficher ou d'enregistrer les plannings de chacun
def print_vacataires(vacataires_dict,save=False):
    week_converter = {'W1': 0, 'W2': 1, 'W3': 2, 'W4': 3}
    day_converter = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'We': 6}
    hour_converter = {'AM': 0, 'PM': 2}

    else_value=0
    data = [
        ["Week 1", f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}",
         f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}"],
        ["Week 2", f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}",
         f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}"],
        ["Week 3", f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}",
         f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}"],
        ["Week 4", f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}",
         f"{else_value}/{else_value}", f"{else_value}/{else_value}", f"{else_value}/{else_value}"],
    ]
    for name,value in vacataires_dict.items():
        loc = name.split("_")
        week = week_converter[loc[1]]
        day = day_converter[loc[2]]
        hour = hour_converter[loc[3]]
        data[week][day] = (data[week][day][:hour] + str(value) + data[week][day][hour + 1:])

    headers = ["Week", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "We"]
    print(f"Emploi du temps des vacataires")
    content = tabulate(data, headers=headers, tablefmt="grid")
    print(content)
    if save:
        with open(f"planning_vacataires.csv", 'w') as file:
            file.write(content)
            file.close()

#Nous passons à la construction du planning à proprement parlé
Planning = Function('Planning',Week,Day,Hour,Nurse,Status)
s = Optimize()

#on implémente la notion de vacataire pour chaque créneau du planning
vacataires = {(semaine,jour,heure):Int(f"vac_{semaine}_{jour}_{heure}")
              for semaine in semaines
              for jour in jours_de_la_semaine
              for heure in heures_de_la_journee}
#le nombre de vacataires pour chaque créneau doit être positif ou nul
for val in vacataires.values():
    s.add(val>=0)

#Un créneau est donnée par une semaine, un jour, une heure. L'emploi du temps est cyclique : on peut toujours calculer un créneau suivant ou précédent
def calc_creneau_suivant(week: Week, day: Day, hour: Hour):
    if hour == AM:
        return week, day, PM
    else:
        if day == J1:
            return week, J2, AM
        elif day == J2:
            return week, J3, AM
        elif day == J3:
            return week, J4, AM
        elif day == J4:
            return week, J5, AM
        elif day == J5:
            return week, We, AM
        else:
            if week == W1:
                return W2, J1, AM
            elif week == W2:
                return W3, J1, AM
            elif week == W3:
                return W4, J1, AM
            else:
                return W1, J1, AM

def calc_creneau_precedent(week: Week, day: Day, hour: Hour):
    if hour == PM:
        return week, day, AM
    else:
        if day == We:
            return week, J5, PM
        elif day == J5:
            return week, J4, PM
        elif day == J4:
            return week, J3, PM
        elif day == J3:
            return week, J2, PM
        elif day == J2:
            return week, J1, PM
        else:
            if week == W4:
                return W3, We, PM
            elif week == W3:
                return W2, We, PM
            elif week == W2:
                return W1, We, PM
            else:
                return W4, We, PM

#Nous avons un certain nombre de contraintes que nous allons implémenter au fur et à mesure

#type 0 : le week-end n'est pas sécable
cstr0 = [If(Planning(semaine,We,AM,infirmiere)==Work,
            Planning(semaine,We,PM,infirmiere)==Work,
            Planning(semaine,We,PM,infirmiere)==Rest)
         for semaine in semaines
         for infirmiere in infirmieres]
s.add(cstr0)

#type 1 : enchainement d'un soir et d'un matin impossible et une journée complète implique une journée complète de repos avant et après
cstr1 = [Implies(Planning(semaine,jour,PM,infirmiere)==Work,
                 Planning(*calc_creneau_suivant(semaine,jour,PM),infirmiere)==Rest)
         for jour in jours_de_la_semaine
         for semaine in semaines
         for infirmiere in infirmieres]
s.add(cstr1)

cstr1Bis = [Implies(
    And(Planning(semaine,jour,AM,infirmiere)==Work,
        Planning(semaine,jour,PM,infirmiere)==Work),
    And(Planning(*calc_creneau_precedent(semaine,jour,AM),infirmiere)==Rest,
        Planning(*calc_creneau_precedent(*calc_creneau_precedent(semaine,jour,AM)),infirmiere)==Rest,
        Planning(*calc_creneau_suivant(semaine,jour,PM),infirmiere)==Rest,
        Planning(*calc_creneau_suivant(*calc_creneau_suivant(semaine,jour,PM)),infirmiere)==Rest))
    for jour in jours_de_la_semaine
    for semaine in semaines
    for infirmiere in infirmieres]
s.add(cstr1Bis)


# type 2 : pas plus de 6 jours de travail consécutif sans journée de repos
def are_the_last_six_days_worked(week: Week, day: Day, nurse: Nurse):
    week_1, day_1, hour_1 = calc_creneau_precedent(week, day, AM)
    week_2, day_2, hour_2 = calc_creneau_precedent(week_1, day_1, AM)
    week_3, day_3, hour_3 = calc_creneau_precedent(week_2, day_2, AM)
    week_4, day_4, hour_4 = calc_creneau_precedent(week_3, day_3, AM)
    week_5, day_5, hour_5 = calc_creneau_precedent(week_4, day_4, AM)
    dates = [(week, day), (week_1, day_1), (week_2, day_2), (week_3, day_3), (week_4, day_4), (week_5, day_5)]

    worked_days = [Or(Planning(w, d, AM, nurse) == Work, Planning(w, d, PM, nurse) == Work) for w, d in dates]
    return Sum([If(worked, 1, 0) for worked in worked_days])


cstr2 = [are_the_last_six_days_worked(semaine, jour, infirmiere) < 6
         for jour in jours_de_la_semaine
         for semaine in semaines
         for infirmiere in infirmieres]
s.add(cstr2)

#type 3 : il faut 3 personnes le matin, 2 personnes le soir, 2 personnes le week-end

cstr3 = [And(
    Sum([If(Planning(semaine,jour,AM,nurse) == Work,1,0)
         for nurse in infirmieres]) + vacataires[(semaine,jour,AM)]==3,
    Sum([If(Planning(semaine,jour,PM,nurse) == Work,1,0)
         for nurse in infirmieres]) + vacataires[(semaine,jour,PM)]== 2)
    for jour in jours_hors_we
    for semaine in semaines]

s.add(cstr3)

cstr3Bis= [And(
    Sum([If(Planning(semaine,We,AM,nurse) == Work,1,0)
         for nurse in infirmieres]) + vacataires[(semaine,We,AM)] ==2,
    Sum([If(Planning(semaine,We,PM,nurse) == Work,1,0)
         for nurse in infirmieres]) + vacataires[(semaine,We,PM)] == 2)
    for semaine in semaines]

s.add(cstr3Bis)

#type 4 : les infirmières doivent travailler exactement 20 demi-journées sur 4 semaines (non glissant)
cstr4 = [Sum([If(Planning(semaine,jour,heure,nurse)==Work,1,0)
              for semaine in semaines
              for jour in jours_hors_we
              for heure in heures_de_la_journee]+[If(Planning(semaine,We,heure,nurse)==Work,2,0)
                                                  for heure in heures_de_la_journee
                                                  for semaine in semaines])==20
         for nurse in infirmieres]

s.add(cstr4)

#on veut un nombre minimal de vacataires dans les emplois du temps
if s.check() == sat:
    solution_planning = s.model()[Planning].as_list()
    model = s.model()
    solution_vacataires = {d.name():model[d] for d in model.decls() if d.name().startswith('vac')}
    print_vacataires(solution_vacataires,save=True)
    for nurse in infirmieres:
        print_planning(solution_planning, nurse,save=True)
else:
    print("unsat")