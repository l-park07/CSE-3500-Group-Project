"""Lookup tables for the NRMP program ids used in the Group 7 CT simulation.

A program id is a 7-digit int: a 4-digit hospital code followed by a 3-digit
specialty code.

    1079140 -> hospital 1079 (Bridgeport Hospital-CT), specialty 140 (Internal Medicine)

The id does not include the NRMP track suffix (the "C0", "C1", ... at the end of
the full program code), so a few ids are shared by more than one categorical
track, for example 1089140C0 and 1089140C1.

Names are taken from "Program Results: Main Residency Match 2021-2025" (NRMP).
Specialty names are the base specialty; track variants such as
"Psychiatry/Research" or "Fam Med/Rural Hungerford Hosp" map to their base
specialty.
"""

# 4-digit hospital code -> hospital name, as listed by NRMP.
HOSPITALS = {
    1079: "Bridgeport Hospital-CT",
    1080: "St Vincents Med Ctr-CT",
    1082: "Greenwich Hospital-CT",
    1083: "Hartford Hospital-CT",
    1085: "St Francis Hospital-CT",
    1087: "Middlesex Hospital-CT",
    1089: "Yale-New Haven Hosp-CT",
    1094: "U Connecticut School of Medicine",
    1095: "Stamford Hospital/Columbia-CT",
    1096: "St Marys Hospital-CT",
    1097: "Waterbury Hospital-CT",
    1977: "Griffin Hospital-CT",
    2186: "Eastern CT Health Network",
    2371: "Quinnipiac Univ/Netter MD SOM-CT",
    2428: "Connecticut Institute for Communities Health",
}

# 3-digit specialty code -> base specialty name.
# Keys are ints, so a code with a leading zero is written without it
# (40 means "040").
SPECIALTIES = {
    40: "Anesthesiology",  # 040
    110: "Emergency Medicine",
    120: "Family Medicine",
    140: "Internal Medicine",
    160: "Neurological Surgery",
    180: "Neurology",
    185: "Child Neurology",
    220: "Obstetrics-Gynecology",
    260: "Orthopaedic Surgery",
    280: "Otolaryngology",
    300: "Pathology",
    320: "Pediatrics",
    340: "Phys Medicine & Rehab",
    362: "Plastic Surgery (Integrated)",
    400: "Psychiatry",
    416: "Interventional Radiology (Integ)",
    440: "General Surgery",
    451: "Vascular Surgery",
    461: "Thoracic Surgery",
    700: "Medicine-Pediatrics",
    751: "Medicine-Preventive Med/General",
}


def split_id(program_id: int) -> tuple[int, int]:
    """Return (hospital_code, specialty_code) for a 7-digit program id."""
    if not 1_000_000 <= program_id <= 9_999_999:
        raise ValueError(f"program id must be 7 digits, got {program_id}")
    return divmod(program_id, 1000)


def hospital_of(program_id: int) -> str:
    """Hospital name for a program id (uses the first four digits)."""
    hospital_code, _ = split_id(program_id)
    return HOSPITALS[hospital_code]


def specialty_of(program_id: int) -> str:
    """Specialty name for a program id (uses the last three digits)."""
    _, specialty_code = split_id(program_id)
    return SPECIALTIES[specialty_code]
