# SI364-Midterm
My application is a way for users to search for recipes based on a search term. The web app will then return a recipe name and a list of ingredients based on that search term and display this along with the user that searched for it on the home page. 

The home page also includes a way for a user to review a recipe with a number 0-5 stars. The other pages show: all the reviews that have been made, all the five star reviews, and the lowest reviewed recipes (0 and 1 stars). 


##ROUTES##
index @app.route('/'):
This route renders the template index.html that extends from base HTML. This template contains two forms. One form, the user inputs their username and display name as well as the recipe search term. Upon submission, the recipe name (based on api), list of ingredients (based on api) and the users username will be added to the same page (using a post request). The same username will not be able to enter the same search term twice without getting a flash message. 

This template also includes the form to submit ratings. The user will enter the recipe name, their username, and rating (0-5 stars). The a user will not be able to enter a review on the same recipe without getting a flash message. 

@app.route('/review_results'):
This route renders the template reviews.html. This route receives data from the reviewform via a GET request from the home page. This page displays the recipe title, rating, and user that made the review for all entered ratings on the form. 

@app.route('/five_stars'):
This route renders the template five_stars.html. It queries from the review db and gets all recipes that have been rated 5 stars. The recipe name and username of the reviewer is displayed as each list item. 

@app.route('/lowest_rated'):
This route renders the template lowest_rated.html. This route queries the review db for ratings that are either 0 or 1 stars and displays the recipe title, rating (0 or 1) and the user that made the review.
