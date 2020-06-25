from flask import Flask, render_template, request, redirect, url_for, flash
from urllib.parse import urlparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import exc
from flask_migrate import Migrate
import requests, random, json, time

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess string'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ingredient.sqlite"

db = SQLAlchemy(app)

Migrate(app, db)



# ==================
# class section
# ==================
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, unique=False, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)

class Limit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, unique=False, nullable=False)
    meal = db.Column(db.Integer, unique=False, nullable=False)
    limit = db.Column(db.Integer, unique=False, nullable=False)


class nofoundError(Exception):
    pass

class atLeastError(Exception):
    pass

class atMostError(Exception):
    pass

# ==================
# handle routers
# ==================

@app.route('/')
def index():

    db.session.query(Ingredient).delete()
    db.session.query(Limit).delete()
    db.session.commit()

    return render_template('index.html')


@app.route('/mealnum', methods=['GET', 'POST'])
def mealnum():

    if request.method == 'POST':
        mealNum = request.form.get('mealNum')
        days = request.form.get('days')
        day = int(days)
        meal = int(mealNum)
        limit = day*meal
        limit = Limit(day=day, meal=meal, limit=limit)
        db.session.add(limit)
        db.session.commit()

        return redirect(url_for('ingredients'))

    else:
        return render_template('mealnum.html')


@app.route('/ingredients')
def ingredients():

        ingPro = Ingredient.query.filter_by(type="pro")
        ingVeg = Ingredient.query.filter_by(type="veg")
        ingCarb = Ingredient.query.filter_by(type="carb")

        return render_template('ingredients.html', ingPro=ingPro, ingVeg=ingVeg, ingCarb=ingCarb)

# ===========================
# add ingredients routes
# ===========================
# 1. check repeated ingredients (DONE)
# 2. check typo (DONE)
# 3. check no result found case (DONE)
@app.route('/addpro', methods=['POST'])
def addpro():
    try:
        added = request.form['protein']
        apiID = '1ddd0896'
        apiKEY = '58ef01156cda25a59462f34755cb565d'
        addURL = "https://api.edamam.com/search?app_id={0}&app_key={1}&q={2}".format(apiID, apiKEY, added)
        # limit check: numer of queries and number of meals
        if( (Limit.query.count()) != 1):
            return redirect(url_for('/'))
        curNum = Ingredient.query.filter_by(type="pro").count()
        if(curNum == Limit.query.first().limit):
            raise atMostError
        # typo & no found check
        foundNum = int(requests.get(addURL).json()['count'])
        if foundNum < 1:
            raise nofoundError
        # repeated check
        ingredient = Ingredient(type="pro", name=request.form['protein'])
        db.session.add(ingredient)
        db.session.commit()

    except nofoundError:
        flash("{} is not a valid input, plase check spelling or pick other protein".format(added))
    
    except atMostError:
        flash("at most {} protein ingredients allow".format(Limit.query.first().limit))

    except exc.SQLAlchemyError as e:
        flash('{} has already been added!'.format(added))
    
    except:
        pass

    finally:
        return redirect(url_for('ingredients'))
    


@app.route('/addveg', methods=['POST'])
def addveg():
    try:
        added = request.form['veg']
        print(added)
        apiID = '1ddd0896'
        apiKEY = '58ef01156cda25a59462f34755cb565d'
        addURL = "https://api.edamam.com/search?app_id={0}&app_key={1}&q={2}".format(apiID, apiKEY, added)
        # limit check: numer of queries and number of meals
        if( (Limit.query.count()) != 1):
            return redirect(url_for('/'))
        curNum = Ingredient.query.filter_by(type="veg").count()
        if(curNum == Limit.query.first().limit):
            raise atMostError
        # typo & no found check
        foundNum = int(requests.get(addURL).json()['count'])
        if foundNum == 0:
            raise nofoundError
        # repeated check
        ingredient = Ingredient(type="veg", name=request.form['veg'])
        db.session.add(ingredient)
        db.session.commit()

    except nofoundError:
        flash("{} is not a valid input, plase check spelling or pick other vegetables".format(added))
    
    except atMostError:
        flash("at most {} vegetabels ingredients allowed".format(Limit.query.first().limit))

    except exc.SQLAlchemyError as e:
        flash('{} has already been added!'.format(added))
    
    except:
        pass

    return redirect(url_for('ingredients'))



@app.route('/addcarb', methods=['POST'])
def addcarb():
    try:
        added = request.form['carbohydrates']
        apiID = '1ddd0896'
        apiKEY = '58ef01156cda25a59462f34755cb565d'
        addURL = "https://api.edamam.com/search?app_id={0}&app_key={1}&q={2}".format(apiID, apiKEY, added)
        # limit check: numer of queries and number of meals
        if( (Limit.query.count()) != 1):
            return redirect(url_for('/'))
        curNum = Ingredient.query.filter_by(type="carb").count()
        if(curNum == Limit.query.first().limit):
            raise atMostError
        # typo & no found check
        foundNum = int(requests.get(addURL).json()['count'])
        if foundNum < 1:
            raise nofoundError
        # repeated check
        ingredient = Ingredient(type="carb", name=request.form['carbohydrates'])
        db.session.add(ingredient)
        db.session.commit()

    except nofoundError:
        flash("{} is not a valid input, plase check spelling or pick other carbohydrates".format(added))
    
    except atMostError:
        flash("at most {} carbohydrates ingredients allowed".format(Limit.query.first().limit))

    except exc.SQLAlchemyError as e:
        flash('{} has already been added!'.format(added))
    
    except:
        flash("something wrong here, please add again")

    return redirect(url_for('ingredients'))


# ===========================
# End of add ingredients routes
# ===========================


@app.route('/generate', methods=['POST','GET'])
def generate():
    try:
        apiID = '1ddd0896'
        apiKEY = '58ef01156cda25a59462f34755cb565d'

        # at least one input check
        pNum = Ingredient.query.filter_by(type="pro").count()
        vNum = Ingredient.query.filter_by(type="veg").count()
        cNum = Ingredient.query.filter_by(type="carb").count()
        if(pNum == 0 or vNum == 0 or cNum == 0):
            raise atLeastError
        
        # corresponding days and meals
        mealNum = Limit.query.first().meal
        dayNum = Limit.query.first().day
        limit = Limit.query.first().limit

        ingDict = generateIngDict()
        #ingredients list - protein
        proList = []
        proDict = {}

        for p in Ingredient.query.filter_by(type="pro").all():
            # apiURL = "https://api.edamam.com/search?app_id={0}&app_key={1}&q={2}&to=14".format(apiID, apiKEY, p.name)
            # result = requests.get(apiURL).json()
            # ingDict[p.name] = result
            proList.append(p.name)

        # if( limit // pNum > 1):
        #     proList = proList*(limit // pNum)
        # proList += proList[:(limit - pNum)]

        # if(mealNum == 1):
        #     day = 1
        #     for pro in proList:
        #         count = int(ingDict[pro]['count'])
        #         if count < 14:
        #             r = random.randint(0, count-1)
        #         else:
        #             r = random.randint(0, 13)
        #         proDict['d{}m1'.format(day)] = ingDict[pro]['hits'][r]['recipe']
        #         day += 1
        # else:
            # day = 1
            # m = 1
            # for pro in proList:
            #     count = int(ingDict[pro]['count'])
            #     if count < 14:
            #         r = random.randint(0, count-1)
            #     else:
            #         r = random.randint(0, 13)
                
            #     if (m == 1):
            #         proDict['d{}m1'.format(day)] = ingDict[pro]['hits'][r]['recipe']['label']
            #         m = 2
            #     else:
            #         proDict['d{}m2'.format(day)] = ingDict[pro]['hits'][r]['recipe']['label']
            #         m = 1
            #         day += 1
                
        
        #ingredients dic - protein
        print('====================================')
        print('====================================')
        print(type(ingDict))
        print(ingDict)
        print('====================================')
        print('====================================')
        
        # extract request datas
        protein = 'chicken breast'
        
        # logic process

        # making api call
        apiURL = "https://api.edamam.com/search?app_id={0}&app_key={1}&q={2}&to=14".format(apiID, apiKEY, protein)
        result = requests.get(apiURL).json()

    except atLeastError:
        flash("at least one input for each category")
        return redirect(url_for('ingredients'))
        
    return render_template('generate.html', protein=protein, apiURL=apiURL, result=result,  mealNum=mealNum, dayNum=dayNum)




# generate ingredient dictionary by calling api
def generateIngDict():

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



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)