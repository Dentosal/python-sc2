def name_normalize(name):
    return name.replace(" ", "").lower()

def name_matches(name1, name2):
    return name_normalize(name1) == name_normalize(name2)
