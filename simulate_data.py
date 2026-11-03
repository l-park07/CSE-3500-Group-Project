"""Simulated match data for the Group 7 Connecticut match.

Builds Program and Applicant objects (the classes in algo.py) from the CT
categorical program table, ct_programs_categorical_2025.csv.

    from simulate_data import generate, summary
    data = generate("ct_programs_categorical_2025.csv", seed=7)
    summary(data)
    data.programs    # list[Program]   rol = applicant ids, best first
    data.applicants  # list[Applicant] rol = Program.ids (1..n), best first
    data.couples     # list[Couple]

Ids follow algo.py: Program.id is a counter starting at 1, and Program.code
is the 7-digit NRMP code. Applicant rank lists hold Program.ids, not codes.
data.program_by_code() maps a 7-digit code to its Program.

How the data is made
--------------------
1. Programs. One Program per 7-digit code. Tracks that share a code
   (e.g. 1089140C0/C1/C2) are merged and their quotas added, so every id
   in a rank list points to exactly one program.

2. Applicants (mode="specialty", the default). Each applicant
     - has a hidden quality score (used only by programs to rank them),
     - picks a first-choice specialty, weighted by how many seats it has,
     - with probability backup_rate also applies to a second specialty,
     - ranks the programs in those specialties by
           program desirability + personal noise
       (first specialty first, backup after), then keeps the top k,
       where k is random in [min_rol, max_rol].
   Program desirability = a shared hospital effect + a small per-program
   effect, so applicants broadly agree on which places are popular but
   don't all submit the same list.

   mode="uniform" is the plain version from the group's notes: each
   applicant ranks k programs chosen completely at random.

3. Program ROLs. A program only ranks applicants who ranked it (mutual
   acceptability, as in the real Match). It orders them by
       applicant quality + program noise
   and, if max_rank_per_seat is set, keeps at most quota * max_rank_per_seat.

Same csv + same seed + same parameters always gives the same data set, so
the group can compare algorithms on identical inputs. save_json/load_json
write and read a data set.
"""

import argparse
import csv
import json
import random
from collections import defaultdict
from dataclasses import dataclass, field

import algo
from algo import Applicant, Couple, Program


@dataclass
class SimData:
    programs: list
    applicants: list
    couples: list = field(default_factory=list)
    params: dict = field(default_factory=dict)

    def program_by_id(self):
        return {p.id: p for p in self.programs}

    def program_by_code(self):
        return {p.code: p for p in self.programs}

    def applicant_by_id(self):
        return {a.id: a for a in self.applicants}


def load_quotas(csv_path):
    """{program id: quota}, merging tracks that share an id."""
    quotas = defaultdict(int)
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            quotas[int(row["id"])] += int(row["quota_2025"])
    return dict(quotas)


def _reset_counters():
    # algo.py numbers objects with module-level counters; start each data set at 1.
    algo.number_programs = 0
    algo.number_applicants = 0
    algo.number_couples = 0


def generate(
    csv_path,
    n_applicants=None,
    applicants_per_seat=1.25,
    seed=0,
    mode="specialty",
    min_rol=1,
    max_rol=10,
    backup_rate=0.3,
    pref_noise=1.0,
    program_noise=0.5,
    max_rank_per_seat=None,
    n_couples=0,
):
    """Build one simulated data set.

    n_applicants       pool size; default round(total seats * applicants_per_seat)
    mode               "specialty" (structured) or "uniform" (fully random lists)
    min_rol, max_rol   bounds on applicant rank-list length
    backup_rate        chance an applicant also ranks a second specialty
    pref_noise         how much applicants disagree about program desirability
    program_noise      how much programs disagree about applicant quality
    max_rank_per_seat  cap on program ROL length as a multiple of quota (None = no cap)
    n_couples          number of couples formed from random pairs of applicants
    """
    if mode not in ("specialty", "uniform"):
        raise ValueError('mode must be "specialty" or "uniform"')
    if not 1 <= min_rol <= max_rol:
        raise ValueError("need 1 <= min_rol <= max_rol")

    rng = random.Random(seed)
    quotas = load_quotas(csv_path)
    program_ids = list(quotas)
    total_seats = sum(quotas.values())
    if n_applicants is None:
        n_applicants = round(total_seats * applicants_per_seat)
    if 2 * n_couples > n_applicants:
        raise ValueError("not enough applicants for that many couples")

    # Program desirability: hospital effect + per-program effect.
    hospital_effect = {}
    desirability = {}
    for pid in program_ids:
        h = pid // 1000
        if h not in hospital_effect:
            hospital_effect[h] = rng.gauss(0, 1)
        desirability[pid] = hospital_effect[h] + 0.5 * rng.gauss(0, 1)

    by_specialty = defaultdict(list)
    seats_by_specialty = defaultdict(int)
    for pid in program_ids:
        by_specialty[pid % 1000].append(pid)
        seats_by_specialty[pid % 1000] += quotas[pid]
    specialties = list(seats_by_specialty)
    weights = [seats_by_specialty[s] for s in specialties]

    def ranked(pids):
        return sorted(
            pids,
            key=lambda p: desirability[p] + pref_noise * rng.gauss(0, 1),
            reverse=True,
        )

    _reset_counters()

    # Programs first, so their ids (1..n) exist before applicants rank them.
    # Each gets its own list; algo.py's rol=[] default would be shared.
    program_of = {code: Program(quotas[code], code, []) for code in program_ids}

    # Applicants: rank lists of program codes, stored as Program.ids.
    applicants = []
    quality = {}
    for _ in range(n_applicants):
        k = rng.randint(min_rol, max_rol)
        if mode == "uniform":
            rol = rng.sample(program_ids, min(k, len(program_ids)))
        else:
            first = rng.choices(specialties, weights)[0]
            rol = ranked(by_specialty[first])
            if len(specialties) > 1 and rng.random() < backup_rate:
                backup = first
                while backup == first:
                    backup = rng.choices(specialties, weights)[0]
                rol += ranked(by_specialty[backup])
            rol = rol[:k]
        a = Applicant(rol=[program_of[code].id for code in rol])
        quality[a.id] = rng.gauss(0, 1)
        applicants.append(a)

    # Program ROLs: rank only the applicants who ranked them.
    applied = defaultdict(list)
    for a in applicants:
        for pid in a.rol:
            applied[pid].append(a.id)

    programs = list(program_of.values())
    for p in programs:
        rol = sorted(
            applied[p.id],
            key=lambda aid: quality[aid] + program_noise * rng.gauss(0, 1),
            reverse=True,
        )
        if max_rank_per_seat is not None:
            rol = rol[: p.quota * max_rank_per_seat]
        p.rol = rol

    # Couples: random pairs. Couple() builds linked_rol from the partners' lists.
    couples = []
    paired = rng.sample(applicants, 2 * n_couples)
    for i in range(0, len(paired), 2):
        couples.append(Couple(paired[i], paired[i + 1]))

    params = dict(
        csv_path=str(csv_path), n_applicants=n_applicants,
        applicants_per_seat=applicants_per_seat, seed=seed, mode=mode,
        min_rol=min_rol, max_rol=max_rol, backup_rate=backup_rate,
        pref_noise=pref_noise, program_noise=program_noise,
        max_rank_per_seat=max_rank_per_seat, n_couples=n_couples,
    )
    return SimData(programs, applicants, couples, params)


def save_json(data, path):
    out = {
        "params": data.params,
        "programs": [{"id": p.id, "code": p.code, "quota": p.quota, "rol": p.rol}
                     for p in data.programs],
        "applicants": [{"id": a.id, "rol": a.rol} for a in data.applicants],
        "couples": [[c.partnerA.id, c.partnerB.id] for c in data.couples],
    }
    with open(path, "w") as f:
        json.dump(out, f)


def load_json(path):
    """Rebuild the objects from save_json output, keeping the same ids."""
    with open(path) as f:
        raw = json.load(f)
    _reset_counters()
    programs = []
    for p in sorted(raw["programs"], key=lambda p: p["id"]):
        obj = Program(p["quota"], p["code"], p["rol"])
        if obj.id != p["id"]:
            raise ValueError("program ids in the file must be 1..n with no gaps")
        programs.append(obj)
    applicants = []
    for a in sorted(raw["applicants"], key=lambda a: a["id"]):
        obj = Applicant(rol=a["rol"])
        if obj.id != a["id"]:
            raise ValueError("applicant ids in the file must be 1..n with no gaps")
        applicants.append(obj)
    by_id = {a.id: a for a in applicants}
    couples = [Couple(by_id[x], by_id[y]) for x, y in raw["couples"]]
    return SimData(programs, applicants, couples, raw["params"])


def summary(data):
    seats = sum(p.quota for p in data.programs)
    lengths = [len(a.rol) for a in data.applicants]
    under = [p for p in data.programs if len(p.rol) < p.quota]
    empty = [a for a in data.applicants if not a.rol]
    print(f"programs: {len(data.programs)}  seats: {seats}")
    print(f"applicants: {len(data.applicants)}  ({len(data.applicants) / seats:.2f} per seat)")
    print(f"applicant ROL length: min {min(lengths)}, "
          f"mean {sum(lengths) / len(lengths):.1f}, max {max(lengths)}")
    print(f"programs ranking fewer applicants than seats: {len(under)}")
    print(f"applicants with an empty ROL: {len(empty)}")
    print(f"couples: {len(data.couples)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Generate a simulated CT match data set.")
    ap.add_argument("--csv", default="ct_programs_categorical_2025.csv")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--applicants", type=int, default=None)
    ap.add_argument("--mode", choices=["specialty", "uniform"], default="specialty")
    ap.add_argument("--couples", type=int, default=0)
    ap.add_argument("--out", default=None, help="write the data set to this JSON file")
    args = ap.parse_args()

    data = generate(args.csv, n_applicants=args.applicants, seed=args.seed,
                    mode=args.mode, n_couples=args.couples)
    summary(data)
    if args.out:
        save_json(data, args.out)
        print(f"saved to {args.out}")
