from gurobipy import Model, GRB, quicksum
from enum import Enum
 
class Group(Enum):
    MATHEMATIK = 1
    PRAKTISCHE_INFORMATIK = 2
    THEORETISCHE_INFORMATIK = 3
    TECHNISCHE_INFORMATIK = 4
    ANWENDUNGSFACH = 5
    SONSTIGE = 6
    WAHLPFLICHT = 7

class Module:
    def __init__(self, name : str, credits : int, grade : int | None, group : Group) -> None:
        self.name = name
        self.credits = credits
        self.grade = grade
        self.group = group

modules = [
    Module("Analysis für Informatiker", 8, 1.3, Group.MATHEMATIK),
    Module("Lineare Algebra für Informatiker", 6, 3.3, Group.MATHEMATIK),
    #Module("Diskrete Strukturen", 6, None, Group.MATHEMATIK),
    Module("Einführung in die angewandte Stochastik", 6, 2.3, Group.MATHEMATIK),
    #Module("Programmierung", 8, None, Group.PRAKTISCHE_INFORMATIK),
    Module("Datenstrukturen und Algorithmen", 8, 1.7, Group.PRAKTISCHE_INFORMATIK),
    Module("Einführung in die Softwaretechnik", 6, 1.0, Group.PRAKTISCHE_INFORMATIK),
    Module("Datenbanken und Informationssysteme", 6, 1.0, Group.PRAKTISCHE_INFORMATIK),
    Module("Formale Systeme, Automaten, Prozesse", 6, 2.3, Group.THEORETISCHE_INFORMATIK),
    Module("Berechenbarkeit und Komplexität", 7, 2.7, Group.THEORETISCHE_INFORMATIK),
    Module("Mathematische Logik", 7, 1.3, Group.THEORETISCHE_INFORMATIK),
    Module("Technische Informatik", 6, 1.0, Group.TECHNISCHE_INFORMATIK),
    Module("Betriebssysteme und Systemsoftware", 6, 2.0, Group.TECHNISCHE_INFORMATIK),
    #Module("Praktikum Systemprogrammierung", 8, None, Group.TECHNISCHE_INFORMATIK),
    Module("Datenkommunikation und Sicherheit", 6, 2.0, Group.TECHNISCHE_INFORMATIK),
    Module("Grundlagen des Managment", 5, 1.0, Group.ANWENDUNGSFACH),
    Module("Quantitative Methoden", 5, 1.7, Group.ANWENDUNGSFACH),
    #Module("Entscheidungslehre", 6, 1.7, Group.ANWENDUNGSFACH),
    #Module("Rechnungswesen", 6, 1.3, Group.ANWENDUNGSFACH),
    #Module("Mentoring", 1, None, Group.SONSTIGE),
    Module("Einführung in das wissenschaftliche Arbeiten (Proseminar)", 3, 1.3, Group.SONSTIGE),
    #Module("Nicht-technisches Wahlfach", 4, None, Group.SONSTIGE),
    Module("Seminar", 5, 1.0, Group.SONSTIGE),
    #Module("Software-Projektpraktikum", 6, None, Group.SONSTIGE),
    Module("Bachelorarbeit und Kolloquium", 15, 1.0, Group.SONSTIGE),
    Module("Compiler Construction", 6, 2, Group.WAHLPFLICHT),
    #Module("Introdution to Artificial Intelligence", 6, 1.3, Group.WAHLPFLICHT),
    #Module("Wahlfach 3", 6, 1.3, Group.WAHLPFLICHT),
    #Module("Wahlfach 4", 6, 1.3, Group.WAHLPFLICHT)
]

def byGroup(modules, group):
    return [m for m in modules if m.group == group]

def solve(modules):
    model = Model("streichtool")
    model.modelSense = GRB.MINIMIZE

    x = {}
    for module in modules:
        x[module.name] = model.addVar(name="x#" + module.name, vtype=GRB.BINARY)

    model.update()

    model.setObjective(
        quicksum(
            (1-x[module.name]) * module.grade
            for module in modules
        ) 
    )

    for g in Group:
        model.addConstr(
            quicksum(x[module.name] for module in byGroup(modules, g))
            <=
            1
        )
    
    model.addConstr(
        quicksum(x[module.name] * module.credits for module in modules)
        <=
        30
    )

    '''model.addConstr(
        x["Bachelorarbeit und Kolloquium"] 
        == 
        0
    )'''

    # optimize
    model.optimize()

    y = sum((1-x[module.name].x) * module.credits * module.grade for module in modules) / sum((1-x[module.name].x) * module.credits for module in modules)
    z = {}
    for module in modules:
        z[module.name] = 0
    # print solution
    if model.status == GRB.OPTIMAL:
        print('\nOptimaler Zielfunktionswert: %g\n' % model.ObjVal)
        for module in modules:
            if x[module.name].x > 0.5 and x[module.name].x * module.grade > y:
                print('Streiche %s aus Bereich %s.' % (module.name, module.group))
                z[module.name] = 1
    else:
        print('Keine Optimalloesung gefunden. Status: %i' % (model.status))
    
    y = sum((1-z[module.name]) * module.credits * module.grade for module in modules) / sum((1-z[module.name]) * module.credits for module in modules)
    print(f"Endnote ist: {y}.")

    return model

solve(modules)