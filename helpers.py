import requests, json

def deleteAllData(db, Ingredient, Limit):
    db.session.query(Ingredient).delete()
    db.session.query(Limit).delete()
    db.session.commit()
    return None


def reachAtMost(tp, Ingredient, Limit):
    
    if( (Limit.query.count()) != 1):
        return redirect(url_for('mealnum'))

    curNum = Ingredient.query.filter_by(type=tp).count()
    if(curNum == Limit.query.first().limit):
        return True

    return False


def atLeastOne(Ingredient):
    pNum = Ingredient.query.filter_by(type="pro").count()
    vNum = Ingredient.query.filter_by(type="veg").count()
    cNum = Ingredient.query.filter_by(type="carb").count()
    if( pNum == 0 or vNum == 0 or cNum == 0 ):
        return False
    return True


def isValidInput(tp, added, db, Ingredient, Limit):
    apiID = '1ddd0896'
    apiKEY = '58ef01156cda25a59462f34755cb565d'
    addURL = "https://api.edamam.com/search?app_id={0}&app_key={1}&q={2}".format(apiID, apiKEY, added)

    callBack = requests.get(addURL).json()
    # reach hit limit
    while('status' in callBack):
            print("waiting api responses")
            time.sleep(3)
            callBack = requests.get(addURL).json()

    count = int(callBack['count'])
    # valide input && store into database
    if count > 0:
        datastr = json.dumps(callBack)
        ingredient = Ingredient(type=tp, name=added, datastr=datastr)
        db.session.add(ingredient)
        db.session.commit()
        return True
    # invalide input
    return False


def generateIngDict1(Ingredient):
    ingDict = {}
    apiID = '1ddd0896'
    apiKEY = '58ef01156cda25a59462f34755cb565d'

    for ing in Ingredient.query.all():
        apiURL = "https://api.edamam.com/search?app_id={0}&app_key={1}&q={2}&to=14".format(apiID, apiKEY, ing.name)
        callBack = requests.get(apiURL).json()
        print(type(callBack))
        # exceeded limit
        while('status' in callBack):
            time.sleep(20)
            callBack = requests.get(apiURL).json()
        # success case
        ingDict[ing.name] = callBack['q']
    return ingDict


def count(Ingredient, tp):
    return Ingredient.query.filter_by(type=tp).count()


def mealNum(Limit):
    return Limit.query.first().meal


def dayNum(Limit):
    return Limit.query.first().day


def limit(Limit):
    return Limit.query.first().limit


def generateList(Ingredient, Limit, tp):
    count = count(Ingredient, tp)
    limit = limit(Limit)

    l = []

    for ing in Ingredient.query.filter_by(type=tp).all():
        l.append(ing.name)
    
    if( limit // count > 1):
        l = l*(limit // count)
    l += l[:(limit - count)]

    return l

    
def ingDict(Ingredient, Limit, tp):
    tpDict = {}
    tpList = generateList(Ingredient, Limit, tp)
    




    return tpDict








