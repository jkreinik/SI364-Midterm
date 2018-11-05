###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import requests
import json
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, ValidationError # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length # Here, too
from flask_sqlalchemy import SQLAlchemy

## App setup code
app = Flask(__name__)
app.debug = True

## All app.config values
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string from si364'

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://jacobkreinik@localhost/jkreinik-midterm"
## Provided:
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)


######################################
######## HELPER FXNS (If any) ########
######################################

def get_or_create_user(username, display_name):
    user_check = User.query.filter_by(username=username).first()
    if user_check is None:
        user = User(username=username, display_name=display_name)
        db.session.add(user)
        db.session.commit()
        return user_check
    else: 
        return user_test

def get_or_create_recipe(user, title, ingredients):
    user_check = Recipes.query.filter_by(user_id=user.id).first()
    title_chec = Reviews.query.filter_by(title=title).first()

    if (user_check & recipe_check):
        recipe = Recipes(title=title, user_id=user.id, ingredients=ingredients).first()
        flash('This Recipe has already been entered... use a different search term')
        return redirect(url_for('index'))
    else: 
        recipe = Recipes(title=title, user_id=user.id, ingredients=ingredients)
        db.session.add(recipe)
        db.session.commit()
        flash('The Recipe has been successfully added!')
        return recipe.first()
    

# def get_or_create_review(user, recipe, rating):
#     user_check = (Reviews.query.filter_by(user_id=user.id).first() 
#     recipe_check = (Reviews.query.filter_by(recipe_id=recipe.id).first() 

#     if (user_check & recipe_check):
#         review = Review(rating=rating, user_id=user.id, recipe_id=recipe.id).first()
#         return review
#     else: 
#         review = Review(rating=rating, user_id=user.id, recipe_id=recipe.id)
#         db.session.add(review)
#         db.session.commit()
#         return review.first()








##################
##### MODELS #####
##################

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64), unique = True)
    display_name = db.Column(db.String(64))
    review = db.relationship('Reviews', backref='users')
    recipes = db.relationship('Recipes', backref='users')

    def __repr__(self):
        return "{} (ID: {})".format(self.username, self.id)



class Recipes(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(64))
    ingredients = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return "Title:{}, Main Ingredient:{} (ID: {})".format(self.title,self.main_ingredient, self.id)


class Reviews(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer,primary_key=True)
    rating = db.Column(db.Integer)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    recipe_id = db.Column(db.Integer,db.ForeignKey('recipes.id'))


    def __repr__(self):
        return "Rating:{} (ID: {})".format(self.rating, self.id)



###################
#### API Call #####
###################

def recipe_api_call(search):
    recipe_baseurl = 'http://www.recipepuppy.com/api/?'
    recipe_fullurl = requests.get(recipe_baseurl, params = {'q': search})
    result = json.loads(recipe_fullurl.text) #object version of omdb dictionary

    return result

def get_recipe_data(recipe_dict):
    all_info = {}
    recipe = recipe_dict['results'][0].items()
    for main in recipe:
        all_info[main[0]] = main[1] 

    all_info['ingredients'] = all_info['ingredients'].split(', ')

    return all_info


def get_recipte_title(all_info_dict):
    title = all_info_dict['title']
    return title

def get_all_ingredients(all_info_dict):
    all_ingr = all_info_dict['ingredients']
    return all_ingr

def get_main_ingredient(all_info_dict):
    all_ingr = all_info_dict['ingredients']
    main_ing = all_ingr[0]
    return main_ing

def get_all_ingr_str(all_info_dict):
    all_ingr = all_info_dict['ingredients']
    ingr_str = ""
    for ingr in all_ingr:
        ingr_str+= ingr + ', '

    return ingr_str


###################
###### FORMS ######
###################

class NameForm(FlaskForm):
    text = StringField('Enter a a type of food, whose recipe you would life to search for (Required): ', validators=[Required(), Length(max=280)])
    username = StringField('Please Enter your Username (Cannot contain spaces)(Required)', validators=[Required(), Length(max=64)])
    display_name = StringField('Enter the name to be displayed (Required, must be at least two words): ', validators=[Required()])
    submit = SubmitField()


class ReviewForm(FlaskForm):
    username = StringField('Please Enter your Username (Cannot Contain Spaces)(Required)', validators=[Required(), Length(max=64)])
    recipe =   StringField('Please Enter the name of the recipe that you want to review(Required)', validators=[Required(), Length(max=128)])
    rating = IntegerField('Enter a rating from 0-5 stars')
    submit = SubmitField()



def validate_username(self, field):
    if self.username.data.split() > 1: 
        raise ValidationError('Invalid username! Usernames must be one word.')

def validate_rating(self, field):
    if self.rating.data > 5 or self.rating.data < 0: 
        raise ValidationError('Invalid rating! ratings must be between 0 and 5')

#######################
###### VIEW FXNS ######
#######################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm() 
    num_recipes = Recipes.query.count()

    if form.validate_on_submit():
        text = form.text.data 
        username = form.username.data 
        display_name = form.display_name.data

        user = get_or_create_user(username,display_name)

        api = recipe_api_call(text)
        recipe_data = get_recipe_data(api)
        ingredients = get_all_ingr_str(recipe_data)
        title = get_recipte_title(recipe_data)

        get_or_create_recipe(user, title, ingredients)

        errors = [v for v in form.errors.values()]
        if len(errors) > 0:
            flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
        return render_template('index.html',form =form, num_recipe = num_recipes)

# @app.route('/recipe', methods=['GET', 'POST'])
# def recipe():
#     form = NameForm(request.form)
#     if request.method == "POST" and form.validate_on_submit():
#         text = form.text.data 
#         username = form.username.data 
#         display_name = form.display_name.data

#         user = get_or_create_user(username,display_name)

#         api = recipe_api_call(text)
#         recipe_data = get_recipe_data(api)
#         ingredients = get_all_ingr_str(recipe_data)
#         title = get_recipte_title(recipe_data)

#         recipe = get_or_create_recipe(user, title, ingredients)

#         errors = [v for v in form.errors.values()]
#         if len(errors) > 0:
#             flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
#         return render_template('recipe.html' num_tweets = num_tweets)









# @app.route('/', methods=['GET', 'POST'])
# def index():
#     form = NameForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
#     # if form.validate_on_submit():
#     #     name = form.name.data
#     #     newname = Name(name)
#     #     db.session.add(newname)
#     #     db.session.commit()
#         #return redirect(url_for('base'))
# return render_template('index.html',form=form)

# @app.route('/names')
# def all_names():
#     names = Name.query.all()
#     return render_template('name_example.html',names=names)




## Code to run the application...

# Put the code to do so here!
if __name__ == '__main__':
    db.create_all() 
    app.run(use_reloader=True,debug=True)

# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
