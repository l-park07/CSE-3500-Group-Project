# NRMP Matching Alogrithm

from itertools import zip_longest # used to iterate and populate couples rol
from collections import deque # used to quickly append/pop item in beg/end of queue
import csv

number_programs = 0
number_applicants = 0
number_couples = 0


def is_match_possible(a, p):
    # returns the object of the one that gets kicked (or 0 if no one moved), returns T/F if match is possible
    if a.couple > 0:
        # couple logic
        pass
    else:
        if (a.id in p.rol): # applicant id of a must be on rol of program p
            if p.get_open_pos() > 0: # open positions
                return 0, True # can add to match without kicking
            
            if len(p.match) > 0: # checking that p.match is not empty
                worst = None
                worst_rank = p.rol.index(a.id)
                for app in p.match: # iterate through matched applicants
                    i_cur = p.rol.index(app.id)
                    if i_cur > worst_rank: # a is preferred to existing match (comparing indices - less index means more preferred)
                        worst_rank = i_cur
                        worst = app
                
                if worst != None:
                    p.match.remove(worst) # removes less preferred candidate from match
                    worst.match = None
                    return worst, True
                else:
                    return 0, False # a is not more preferred to current apps matched
    return 0, False # a cannot be matched



def is_match_confirmed(a, p):
    # already known that a can be added, determining if it is tentative or confirmed match
    a_rank = p.rol.index(a.id) + 1
    if(a_rank <= p.quota):
        return True
    return False


    
def make_tent_match(Tentative, a, p):
    # queue -> tentative
    Tentative.append(a)
    p.match.append(a)
    a.match = p
    return Tentative



def make_confirmed_match(Confirmed, a, p):
    # match to be made (only executes when confirmed)
    # direct from queue -> confirmed
    # CHECK p.get_open_pos() > 0 (already checked if get to this point)
    Confirmed.append(a)
    p.match.append(a)
    a.match = p
    return Confirmed



def make_unmatched(Unmatched, a):
    a.match = None
    Unmatched.append(a)
    return Unmatched


def rematch(a, p):
    # will take removed applicant and try to re place them
    # OPTIONS (for placement): tent->tent; tent->unmatched (-1); tent->confirmed (1)
    cur = a.rol.index(p.id) + 1 # pick up where you left off
    for i in range(cur, len(a.rol)):
        program = ProgramID[a.rol[i]]
        x, pos = is_match_possible(a, program)
        if(pos):
            if(is_match_confirmed(a,program)):
                return x, 1, program
            return x, 0, program
    # -1 -> goes to unmatched, 1 -> confirmed, 0 -> stayed as a tentative match
    return 0, -1, None
# CHECK THIS - RECURSION MAY NOT EDIT PLACE/TENT







'''Data classes for Program, Applicant, Couple'''
class Program:
    # program class
    def __init__(self, q, code=-1, rol=[]):
        global number_programs 
        number_programs += 1

        self.id = number_programs # integer, will start at 1 (reference this instead of code for applicant rol)
        self.code = code # represented by #### ### (length 7 integer) which will never have leading zeros
        self.quota = q # integer, quota of program (number of spots to fill)
        self.rol = rol # ranked order list of program (ranking applicants) - stores applicant IDs
        self.match = [] # matched applicants, stores applicant OBJECTS
        self._open = self.quota

    def code_decoder(self):
        # decodes and ouputs self.id as the hospital name, specialty and self.quota (maybe positions open?)
        pass

    def get_open_pos(self):
        self._open = self.quota - len(self.match) # gives how many positions are currently open
        return self._open



class Applicant: 
    # applicant class
    def __init__(self, rol=[], couple=-1):
        global number_applicants
        number_applicants += 1

        self.id = number_applicants #integer
        self.rol = rol # ranked order list of applicant (ranking programs- stores Program.ids)
        self.couple = couple # integer: -1 indicates not a couple, otherwise it is same as couple.id
        self.match = None
    def matched(self, program):
        self.match = program #program object (then can decode) -- MAYBE HAVE AS ADD'L VARIABLE? self.hospital, self.specialty



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
#Programs = [Program(2), Program(2)]
#Applicants = [Applicant([1,2]), Applicant([2])] # should this be ids or object instances



'''Data Class structures'''
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
        


Applicants = [] # WILL BE LIST OF APPLICANT OBJECTS
Programs = [] # WILL BE LIST OF PROGRAM OBJECTS 
ProgramID = {}
ApplicantID = {}


Tent = [] # where the tentative matches will go (initially empty), can write, SHOULD BE EMPTY AT END
Confirmed = [] # only add, do not remove from
Unmatched = [] # only add, do not remove from (once added to unmatched, means that no possible match could be found for an applicant)

queue = Queue() # initialized with all applicants 
for x in Applicants:
    queue.enqueue(x) # add all applicants to queue


# if someone gets kicked out, return id of the person who got removed (while match(self,id) != 0)
    
while(queue.size() != 0):
    a = queue.peek() # get first Applicant in queue
    for p_id in a.rol: # ids of program
        p = ProgramID[p_id]
        removed, possible = is_match_possible(a,p) # removed either stores app object or 0
        if possible:
            if is_match_confirmed(a,p):
                Confirmed = make_confirmed_match(Confirmed, a, p)
            else:
                Tent = make_tent_match(Tent, a, p)
            removed_from_p = p
            while(removed != 0): # if not 0, then someone got kicked
                Tent.remove(removed)
                r, outcome, new_p = rematch(removed, removed_from_p) # removed is Applicant object
                if outcome == -1:
                    Unmatched = make_unmatched(Unmatched, removed)
                elif outcome == 1:
                    Confirmed = make_confirmed_match(Confirmed, removed, new_p)
                else:
                    Tent = make_tent_match(Tent, removed, new_p)
                removed = r
                removed_from_p = new_p
            break
    else: 
        Unmatched = make_unmatched(Unmatched, a)
    queue.dequeue()
    # determine if match is possible for first element in queue
    # use peek to access most recent element
    # if match not possible, move on to next in ROL
    # if match is possible but kicks someone out, now should find new match for that person
    # if match is possible and tentative, add to tent (update all accd values)


assert [x.id for x in Tent] == [1]       # A1 is still tentative at this point
assert [x.id for x in Confirmed] == [2]  # only A2 is confirmed so far

# after queue is empty (make all tent matches final)
for y in Tent:
    Confirmed.append(y) # y already has its match, making it confirmed
Tent.clear()

# tent and queue should now be empty


'''
test inputs:

# ---- TEST 1: kick chain + rematch + unmatched ----
Programs = [Program(1, rol=[2, 1, 3]),   # P1 (quota 1) prefers A2 > A1 > A3
            Program(1, rol=[1, 3])]      # P2 (quota 1) prefers A1 > A3
Applicants = [Applicant(rol=[1, 2]),     # A1
              Applicant(rol=[1]),        # A2
              Applicant(rol=[2, 1])]     # A3
ProgramID = {p.id: p for p in Programs}
ApplicantID = {a.id: a for a in Applicants}

# ---- TEST 2: leftover tentative gets finalized ----
Programs = [Program(2, rol=[3, 2, 1])]   # applicant 3 ranked first but never applies
Applicants = [Applicant(rol=[1]), Applicant(rol=[1])]
ProgramID = {p.id: p for p in Programs}
ApplicantsID = {a.id: a for a in Applicants}
# expected: A2 (rank 2 <= quota 2) confirmed immediately,
# A1 (rank 3) tentative until the end, then moved to Confirmed
# after the match: len(Tent) == 0, sorted(x.id for x in Confirmed) == [1, 2], Unmatched == []


checking tests:
def matched_id(a):
    return a.match.id if a.match else None

assert [matched_id(a) for a in Applicants] == [1, 1]
assert [sorted(x.id for x in p.match) for p in Programs] == [[1, 2]]
assert len(Tent) == 0
assert sorted(x.id for x in Confirmed) == [1, 2]
assert Unmatched == []
print("test 2 passed")

assert [matched_id(a) for a in Applicants] == [2, 1, None]
assert [[x.id for x in p.match] for p in Programs] == [[2], [1]]
assert len(Tent) == 0
assert sorted(x.id for x in Confirmed) == [1, 2]
assert [x.id for x in Unmatched] == [3]
print("test 1 passed")





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