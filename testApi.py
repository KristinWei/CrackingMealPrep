from flask import Flask, render_template, request, redirect, url_for, flash
from urllib.parse import urlparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import exc
from flask_migrate import Migrate
from helpers import *
import requests, random, json, time, ast

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess string'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ingredient.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

Migrate(app, db)

# ==================
# class section
# ==================
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, unique=False, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    datastr = db.Column(db.String, unique=False, nullable=True)


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

    deleteAllData(db, Ingredient, Limit)
    return render_template('index.html')


@app.route('/mealnum', methods=['GET', 'POST'])
def mealnum():
    deleteAllData(db, Ingredient, Limit)

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

@app.route('/add', methods=['POST'])
def add():
    try:
        if 'pro' in request.form:
            added = request.form['pro']
            tp = "pro"
            print(added)
        elif 'veg' in request.form:
            added = request.form['veg']
            tp = "veg"
        else:
            added = request.form['carb']
            tp = "carb"

        # maximum inputs check
        if( reachAtMost(tp, Ingredient, Limit) ):
            raise atMostError

        # typo & no found & repeat check
        if ( not isValidInput(tp, added, db, Ingredient, Limit) ):
            raise nofoundError
    
    except atMostError:
        flash("at most {} protein ingredients allow".format(Limit.query.first().limit))

    except nofoundError:
        flash("{} is not a valid input, plase check spelling or pick other protein".format(added))
    
    except exc.SQLAlchemyError as e:
        flash('{} has already been added!'.format(added))
    
    except:
        redirect(url_for('mealnum'))

    finally:
        return redirect(url_for('ingredients'))


# ===========================
# End of add ingredients routes
# ===========================
@app.route('/generate', methods=['POST','GET'])
def generate():
    try:
        if( not atLeastOne(Ingredient) ):
            raise atLeastError

        proRcp = recipeDict(Ingredient, Limit, 'pro')
        vegRcp = recipeDict(Ingredient, Limit, 'veg')
        carbRcp = recipeDict(Ingredient, Limit, 'carb')

    except atLeastError:
        flash("at least one input for each category")
        return redirect(url_for('ingredients'))
        
    return render_template('generate.html', mealNum=mealNum(Limit), dayNum=dayNum(Limit), pr=proRcp, vr=vegRcp, cr=carbRcp)



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)

 