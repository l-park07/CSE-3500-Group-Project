# NRMP Matching Alogrithm

from itertools import zip_longest # used to iterate and populate couples rol
from collections import deque # used to quickly append/pop items in beg/end of queue


number_programs = 0
number_applicants = 0
number_couples = 0


class Program:
    # program class
    def __init__(self, q, id=0, rol=[]):
        global number_programs 
        number_programs += 1

        self.id = id # represented by #### ### (length 7 integer) which will never have leading zeros
        self.quota = q # integer, quota of program (number of spots to fill)
        self.rol = rol # ranked order list of program (ranking applicants)
        self.match = []

    def code_decoder(self):
        # decodes and ouputs self.id as the hospital name, specialty and self.quota (maybe positions open?)
        pass
        

    def match(self, id): # id of applicant
        # will determine whether match is possible
        # if possible, added to match (kicking out someone if needed, updating quota as needed)
        # if not possible, return 0
        # if someone gets kicked out, return id of the person who got removed (while match(self,id) != 0)
        pass



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



# will need to load data and create/store applicant/program instances in array
programs = [Program(2), Program(2)]
applicants = [Applicant([1,2]), Applicant([2])] # should this be ids or object instances
# orrr applicants = [1,2,3]
# and applicant_dict = {1: Applicant([1,2]), 2: A....}

class Queue:
    def __init__(self):
        self._items = deque()

    def enqueue(self, applicant):
        self._items.append(applicant)

    def dequeue(self):
        return self._items.popleft()

    def peek(self):
        # return first item without removing it
        return self._items[0]

    def size(self):
        return len(self._items)


class Tentative:
    def __init__(self):
        self._items = deque()
    # will add add'l behavior as needed

    def make_confirmed(self, confirmed):
        # move all tent matches to confirmed array (return confirmed array)
        pass


confirmed = [] # only add, do not remove from
unmatched = [] # only add, do not remove from (once added to unmatched, means that no possible match could be found for an applicant)



# should it be applicant instances or just plain applicant ids?



'''
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
'''