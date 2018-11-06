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

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://jacobkreinik@localhost/si364midterm"
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
        return user
    else: 
        return user_check

def get_or_create_recipe(user, title, ingredients):
    recipe_check = Recipes.query.filter_by(user_id=user.id, title=title).first()

    if recipe_check:
        flash('This Recipe has already been entered... use a different search term')
        return redirect(url_for('index'))
    else: 
        recipe = Recipes(title=title, user_id=user.id, ingredients=ingredients)
        db.session.add(recipe)
        db.session.commit()
        flash('The Recipe has been successfully added!')
        return recipe
    
def get_or_create_review(username, recipe_name, rating):
    rating_check = Reviews.query.filter_by(username=username, recipe_name=recipe_name).first()

    if rating_check:
        flash('This user has already reviewed this recipe... choose a diferent recipe to review')
        return redirect(url_for('index'))
    else: 
        review = Reviews(recipe_name=recipe_name, username=username, rating=rating)
        db.session.add(review)
        db.session.commit()
        flash('The Recipe has been successfully reviewed!')
        return review



##################
##### MODELS #####
##################

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64), unique = True)
    display_name = db.Column(db.String(64))
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
    recipe_name = db.Column(db.String())
    username = db.Column(db.String())


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
    form2 = ReviewForm()
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
        print(user)
        get_or_create_recipe(user, title, ingredients)

        errors = [v for v in form.errors.values()]
        if len(errors) > 0:
            flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))

        errors2 = [v for v in form2.errors.values()]
        if len(errors) > 0:
            flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))

    user_recipe_data = []
    for x in Recipes.query.all():
        recipe_title = x.title
        recipe_ingredients = x.ingredients
        user_info = User.query.filter_by(id=x.user_id).first()
        user_recipe_data.append((recipe_title,recipe_ingredients,user_info))

    return render_template('index.html',form =form,form2=form2, num_recipe = num_recipes, user_recipe = user_recipe_data)



@app.route('/review_results', methods=['GET', 'POST'])
def review_results():
    if request.args:
        username = request.args.get('username')
        recipe_name = request.args.get('recipe')
        rating_num = request.args.get('rating')

        get_or_create_review(username,recipe_name, rating_num)

    review_data = []
    for x in Reviews.query.all():
        username_db = x.username
        recipe_name_db = x.recipe_name
        rating_db = x.rating
        review_data.append((recipe_name_db,rating_db,username_db))

    return render_template('reviews.html', review_data=review_data)
        

@app.route('/five_stars', methods=['GET', 'POST'])
def five_stars():
    five_star_lst = []
    five_star_reviews = Reviews.query.filter_by(rating=5).all()
    for x in five_star_reviews:
        recipe_name = x.recipe_name
        username = x.username
        five_star_lst.append((recipe_name, username))

    return render_template('five_stars.html', five_star_lst=five_star_lst)


@app.route('/lowest_rated', methods=['GET', 'POST'])
def lowest_rated():
    low_star_lst = []
    low_reviews = Reviews.query.filter(Reviews.rating.in_([0,1])).all()
    for x in low_reviews:
        recipe_name = x.recipe_name
        username = x.username
        rating = x.rating
        low_star_lst.append((recipe_name, username, rating))

    return render_template('lowest_rated.html', low_star_lst=low_star_lst)


## Code to run the application...

# Put the code to do so here!
if __name__ == '__main__':
    db.create_all() 
    app.run(use_reloader=True,debug=True)

# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
