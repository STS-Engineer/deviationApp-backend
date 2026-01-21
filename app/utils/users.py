# List of users by role
COMMERCIAL_USERS = [
    {"name": "Dean HAYWARD", "email": "dean.hayward@avocarbon.com"},
    {"name": "James MCCRONE", "email": "james.mccrone@avocarbon.com"},
    {"name": "Franck LAGADEC", "email": "franck.lagadec@avocarbon.com"},
    {"name": "Martin ZACNY", "email": "martin.zacny@avocarbon.com"},
    {"name": "Souheil YAACOUBI", "email": "souheil.yaacoubi@avocarbon.com"},
    {"name": "Marion SPICKER", "email": "marion.spicker@avocarbon.com"},
    {"name": "Eipe THOMAS", "email": "eipe.thomas@avocarbon.com"},
    {"name": "Ramkumar PARTHASARATHI", "email": "ramkumar.p@avocarbon.com"},
    {"name": "Selvakumar KUMARESAN", "email": "selvakumar.k@avocarbon.com"},
    {"name": "John CHRISTOPHER", "email": "john.christopher@avocarbon.com"},
    {"name": "Vadivukkarasi SUBRAMANIYAN", "email": "vadivukkarasi.s@avocarbon.com"},
    {"name": "Parimmal PATKKI", "email": "parimmal.patkki@avocarbon.com"},
    {"name": "Tao REN", "email": "tao.ren@avocarbon.com"},
    {"name": "Samtak JOO", "email": "samtak.joo@avocarbon.com"},
    {"name": "Youngjin PARK", "email": "youngjin.park@avocarbon.com"},
    {"name": "Junghwan YU", "email": "junghwan.yu@avocarbon.com"},
    {"name": "Allen TAO", "email": "allen.tao@avocarbon.com"},
    {"name": "Mark ZHANG", "email": "jianguo.zhang@avocarbon.com"},
    {"name": "William REN", "email": "eric.ren@avocarbon.com"},
    {"name": "Alice CHEN", "email": "alice.chen@avocarbon.com"},
    {"name": "Austin YUAN", "email": "austin.yuan@avocarbon.com"},
    {"name": "Felix WANG", "email": "felix.wang@avocarbon.com"},
]

PL_USERS = [
    {"name": "Allan RIEGEL (Chokes, Assemblies)", "email": "allan.riegel@avocarbon.com"},
    {"name": "Cedric BOUVIER (Brushes)", "email": "cedric.bouvier@avocarbon.com"},
]

VP_USERS = [
    {"name": "Olivier SPICKER (VP)", "email": "olivier.spicker@avocarbon.com"},
    {"name": "Eric SUSZYLO (VP)", "email": "eric.suszylo@avocarbon.com"},
]

# Test user - accessible for all roles
TEST_USER = {"name": "Rihem ARFAOUI (Test)", "email": "rihem.arfaoui@avocarbon.com"}


def get_users_by_role(role: str):
    """Get list of users for a specific role"""
    if role.upper() == "COMMERCIAL":
        return COMMERCIAL_USERS + [TEST_USER]
    elif role.upper() == "PL":
        return PL_USERS + [TEST_USER]
    elif role.upper() == "VP":
        return VP_USERS + [TEST_USER]
    return []
