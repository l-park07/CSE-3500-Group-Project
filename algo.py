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



class Applicant: 
    # applicant class
    def __init__(self, rol=[], couple=-1):
        global number_applicants
        number_applicants += 1

        self.id = number_applicants #integer
        self.rol = rol # ranked order list of applicant (ranking programs)
        self.couple = couple # integer: -1 indicates not a couple, otherwise it is same as couple.id
        self.match = None
    def matched(self, program):
        self.match = program



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
Programs = [Program(2), Program(2)]
Applicants = [Applicant([1,2]), Applicant([2])] # should this be ids or object instances
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

    def confirmed_match(self, confirm, ls, p):
        # assumes that check has already been done and there is no way for 'confirm' applicant to not match with any other program (or get kicked out)
        ls.append(confirm)
        p.match.append(confirm)
        p.quote -= 1
        confirm.matched(p) # update match
        


class Tentative:
    def __init__(self):
        self._items = deque()
    # will add add'l behavior as needed

    def make_confirmed(self, confirmed, ls, p): # confirmed:applicant object; ls:Confirmed array; p:program object
        # move tent match to confirmed array (return confirmed array)
        ls.append(confirmed) # adds confirmed applicant to ls (Confirmed)
        p.match.append(confirmed)
        p.quota -= 1
        confirmed.matched(p) # pass program object to confirmed (applicant object) 
        return ls


Confirmed = [] # only add, do not remove from
Unmatched = [] # only add, do not remove from (once added to unmatched, means that no possible match could be found for an applicant)

Queue = Queue() # initialized with all applicants 
for x in Applicants:
    Queue.enqueue(x) # add all applicants to Queue

Tent = Tentative() # where the tentative matches will go (initially empty)

# will determine whether match is possible
        # if possible, added to match (kicking out someone if needed, updating quota as needed)
        # if not possible, return 0
        # if someone gets kicked out, return id of the person who got removed (while match(self,id) != 0)
    
while(Queue != 0):
    # determine if match is possible for first element in queue
    # use peek to access most recent element
    # if match not possible, move on to next in ROL
    # if match is possible but kicks someone out, now should find new match for that person
    # if match is possible and tentative, add to tent (update all accd values)
    pass

# must be applicant instances pass I think

# after queue is empty (make all tent matches final)
for y in Tent:
    Confirmed.append(y) # y already has its match and program already has 


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