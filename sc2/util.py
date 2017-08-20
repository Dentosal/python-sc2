def name_normalize(name):
    return name.replace(" ", "").lower()

def name_matches(name1, name2, exact=True):
    n1 = name_normalize(name1)
    n2 = name_normalize(name2)

    return n1 == n2 or (not exact and (n1.startswith(n2) or n2.startswith(n1)))
