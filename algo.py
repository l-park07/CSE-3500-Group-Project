# NRMP Matching Alogrithm

from itertools import zip_longest # used to iterate and populate couples rol

number_programs = 0
number_applicants = 0
number_couples = 0

class Program:
    # program class
    def __init__(self, q, rol=[]):
        global number_programs 
        number_programs += 1

        self.id = number_programs # integer
        self.quota = q # integer, quota of program (number of spots to fill)
        self.rol = rol # ranked order list of program (ranking applicants)
        self.match = []

class Applicant: 
    # applicant class
    def __init__(self, rol=[], couple=-1):
        global number_applicants
        number_applicants += 1

        self.id = number_applicants #integer
        self.rol = rol # ranked order list of applicant (ranking programs)
        self.couple = couple # integer: -1 indicates not a couple, otherwise it is same as couple.id

class Couple:
    # couple class
    def __init__(self, app1, app2):
        global number_couples
        number_couples += 1
        self.couple_id = number_couples # integer, couple id
        app1.couple = self.couple_id
        app2.couple = self.couple_id
        self.partnerA = app1 # applicant object
        self.partnerB = app2 # applicant object
        

        self.linked_rol = list(zip_longest(self.partnerA.rol, self.partnerB.rol, fillvalue=0))


# testing....
a = Applicant([1,2,3])
b = Applicant([3,2])

print(f"number of couples: {number_couples},\n number of applicants: {number_applicants},\n number of programs: {number_programs}\n")
print(f"applicant a: {a.id} = {a.rol}, is a couple?? answeR: {a.couple}\n")

couple = Couple(a,b)

print(f"number_couples: {number_couples}, number of applicants: {number_applicants}, number of programs: {number_programs}\n")
print(f"applicant a: {a.id} = {a.rol}, is a couple?? answeR: {a.couple}")
print(f"applicant b: {b.id} = {b.rol}, is a couple?? answeR: {b.couple}")
print(f"couple 1: {couple.couple_id}\n\tlist: {couple.linked_rol}")
