from flask import Flask, render_template, request, redirect, url_for
from urllib.parse import urlparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import exc
import requests


app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess string'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ingredient.sqlite"
db = SQLAlchemy(app)

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, unique=False, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)


@app.route('/')
def index():
    db.session.query(Ingredient).delete()
    db.session.commit()
    return render_template('index.html')


@app.route('/ingredients')
def ingredients():

    mealNum = request.args.get('mealNum')
    days = request.args.get('days')

    try:
        ingPro = Ingredient.query.filter_by(type="pro")
    except exc.SQLAlchemyError as e:
        print(type(e))

    try:
        ingVeg = Ingredient.query.filter_by(type="veg")
    except exc.SQLAlchemyError as e:
        print(type(e))

    try:
        ingCarb = Ingredient.query.filter_by(type="carb")
    except exc.SQLAlchemyError as e:
        print(type(e))


    return render_template('ingredients.html',mealNum=mealNum, days=days, 
                            ingPro=ingPro, ingVeg=ingVeg, ingCarb=ingCarb)


# ===========================
# add ingredients routes
# ===========================
@app.route('/addpro', methods=['POST'])
def addpro():
    try:
        ingredient = Ingredient(type="pro", name=request.form['protein'])
        db.session.add(ingredient)
        db.session.commit()
    except exc.SQLAlchemyError as e:
        print(type(e))
    return redirect(url_for('ingredients'))


@app.route('/addveg', methods=['POST'])
def addveg():
    try:
        ingredient = Ingredient(type="veg", name=request.form['vagetables'])
        db.session.add(ingredient)
        db.session.commit()
    except exc.SQLAlchemyError as e:
        print(type(e))
    
    return redirect(url_for('ingredients'))



@app.route('/addcarb', methods=['POST'])
def addcarb():
    try:
        ingredient = Ingredient(type="carb", name=request.form['carbohydrates'])
        db.session.add(ingredient)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    return redirect(url_for('ingredients'))



    
@app.route('/generate', methods=['POST'])
def generate():

    # extract request datas
    protein = request.args.get('protein')
    mealNum = request.args.get('mealNum')
    days = request.args.get('days')


    # logic process

    # making api call
    apiID = '1ddd0896'
    apiKEY = '58ef01156cda25a59462f34755cb565d'
    apiURL = "https://api.edamam.com/search?app_id={0}&app_key={1}&q={2}&to=14".format(apiID, apiKEY, protein)
    result = requests.get(apiURL).json()

    return render_template('generate.html', protein=protein, apiURL=apiURL, result=result)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)