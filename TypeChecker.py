def isfloat(x):
    try:
        float(x)
        return True
    except Exception as e:
        print (e)
        return False