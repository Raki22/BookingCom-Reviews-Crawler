from re import compile

def serialize_name(value):
    return value.strip(" \n")

def serialize_stars(value):
    if type(value) is int:
        return value
    else:
        nbrPtrn = compile(r'[^0-9]')
        value = nbrPtrn.sub('', value)
        if value == '':
            return 0
        else:
            return int(value)

def serialize_nbrReviews(value):
    nbrPtrn = compile(r'[^0-9]')
    value = nbrPtrn.sub('', value)
    if value == '':
        return 0
    else:
        return int(value) 

def serialize_ratingScore(value):
    if value == '':
        return 0.0
    else:
        return float(value.strip())

def serialize_ratingLabel(value):
    return value.strip()

def serialize_nationality(value):
    return value.strip(" \n")

def serialize_personalScore(value):
    if value == '':
        return 0.0
    else:
        return float(value.strip())

def serialize_reviewTitle(value):
    return value.strip(" \n")

def serialize_positivePart(value):
    return value.strip(" \n")

def serialize_negativePart(value):
    return value.strip(" \n")
