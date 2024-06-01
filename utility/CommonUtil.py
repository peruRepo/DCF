
def isFloat(value):
    try:
        float(value)
        if float(value) <= 0 or float(value) > 0:
            return True
        else:
            return False
    except ValueError:
        return False