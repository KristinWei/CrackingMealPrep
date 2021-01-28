import requests, json, random, time
from decimal import Decimal

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
    if(tp == "veg"):
        addURL = "https://api.edamam.com/search?app_id={0}&app_key={1}&q={2}&to=100&diet=low-carb&health=vegan".format(apiID, apiKEY, added)
    elif (tp == 'carb'):
        addURL = "https://api.edamam.com/search?app_id={0}&app_key={1}&q={2}&to=100&&health=vegetarian".format(apiID, apiKEY, added)
    else:
        addURL = "https://api.edamam.com/search?app_id={0}&app_key={1}&q={2}&to=100&diet=high-protein".format(apiID, apiKEY, added)

    callBack = requests.get(addURL).json()
    # reach hit limit
    while('status' in callBack):
            print("waiting api responses")
            print(callBack['status'])
            time.sleep(2)
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


def count(Ingredient, tp):
    return Ingredient.query.filter_by(type=tp).count()


def mealNum(Limit):
    return Limit.query.first().meal


def dayNum(Limit):
    return Limit.query.first().day


def limitNum(Limit):
    return Limit.query.first().limit


def generateList(Ingredient, Limit, tp):
    ct = count(Ingredient, tp)
    limit = limitNum(Limit)

    l = []

    for ing in Ingredient.query.filter_by(type=tp).all():
        l.append(ing.name)
    
    if( limit // ct > 1):
        l = l*(limit // ct)
    l += l[:(limit - ct)]

    return l


def randomNum(count):

    if count < 100:
        r = random.randint(0, count-1)
    else:
        r = random.randint(0, 99)
    return r


def processNumber(recipeDict):
    recipeDict['yield'] = int(recipeDict['yield'])
    y = recipeDict['yield']
    recipeDict['calories'] = int(recipeDict['calories'] / y)
    recipeDict['totalWeight'] = int(recipeDict['totalWeight'] / y)

    recipeDict['ingNum'] = len(recipeDict['ingredientLines'])

    for key, value in recipeDict['totalNutrients'].items():
        value['quantity'] = int(value['quantity'] / y)
    
    for key, value in recipeDict['totalDaily'].items():
        value['quantity'] = int(value['quantity'] / y)
    
    # recipeDict['cuisineType'] = json.dumps(recipeDict['cuisineType']);
    

    return recipeDict


def oneMealDict(Ingredient, Limit, tpList):
    day = 1
    result = {}

    for ing in tpList:
        datastr = Ingredient.query.filter_by(name=ing).first().datastr
        data = json.loads(datastr)

        count = int(data['count'])
        r = randomNum(count)
        
        if(day <= dayNum(Limit)):
            # store recipe label for now
            result['d{}m1'.format(day)] = data['hits'][r]['recipe']
            result['d{}m1'.format(day)] = processNumber(result['d{}m1'.format(day)])
            day += 1

    return result
        

def twoMealDict(Ingredient, Limit, tpList):
    m =1
    day = 1
    result = {}

    for ing in tpList:
        datastr = Ingredient.query.filter_by(name=ing).first().datastr
        data = json.loads(datastr)

        # generate a random index number
        count = int(data['count'])
        r = randomNum(count)
        
        # generate recipe
        if(day <= dayNum(Limit)):
            if( m == 1):
                result['d{}m1'.format(day)] = data['hits'][r]['recipe']
                result['d{}m1'.format(day)] = processNumber(result['d{}m1'.format(day)])
                m = 2
            else:
                result['d{}m2'.format(day)] = data['hits'][r]['recipe']
                result['d{}m1'.format(day)] = processNumber(result['d{}m1'.format(day)])
                m = 1
                day += 1
        
    return result


def recipeDict(Ingredient, Limit, tp):

    tpList = generateList(Ingredient, Limit, tp)
    meal = mealNum(Limit)

    if (meal == 1):
        return oneMealDict(Ingredient, Limit, tpList)
    else:
        return twoMealDict(Ingredient, Limit, tpList)








