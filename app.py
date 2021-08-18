import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

# Credit: Code taken from Task Manger (linked in README.md) and edited to suit project needs.

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


# Recipes
@app.route("/")
@app.route("/get_recipe")
def get_recipes():
    recipes = list(mongo.db.recipes.find())
    return render_template("recipes.html", recipes=recipes)


# Recipes
@app.route("/recipe/<recipe_id>")
def recipesingle(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("recipe.html", recipe=recipe)


# Search for Recipes
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    print(query)
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    return render_template("recipes.html", recipes=recipes)


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #check user is already in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if existing_user:
            #ensure passed word matches 
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))
                
            else:
                #invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesnt exist
            flash("Incorrect username and/or Password")

    return render_template("login.html")


# Profile 
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # get the session user's username from the database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    recipes = list(mongo.db.recipes.find({"created_by": session["user"]}))
    return render_template("profile.html", username=username, recipes=recipes)
    
    if session["user"]:
        return render_template("profile.html", username=username)
    
    return redirect(url_for("login"))


# Logout
@app.route("/logout")
def logout():
    #remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


# Add Recipe 
@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        recipe = {
            "category_name": request.form.get("category_name"),
            "recipe_name": request.form.get("recipe_name"),
            "ingredients": request.form.get("ingredients"),
            "serves": request.form.get("serves"),
            "method": request.form.get("method"),
            "created_by": session["user"],
            "recipe_image": request.form.get('image')
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe Sucessfully Added")
        return redirect(url_for("add_recipe"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipe.html", categories=categories)


# Edit Recipe 
@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name"),
            "recipe_name": request.form.get("recipe_name"),
            "ingredients": request.form.get("ingredients"),
            "serves": request.form.get("serves"),
            "method": request.form.get("method"),
            "created_by": session["user"],
            "recipe_image": request.form.get('image')
        }
        mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, submit)
        flash("Recipe Sucessfully Updated")

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_recipe.html", recipe=recipe, categories=categories)


# Delete Recipe 
@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Recipe Successfully Deleted")
    return redirect(url_for("get_recipes"))


# Categories 
@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


# Add Categoies 
@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")


# Edit Category 
@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category Successfully Updated")
        return redirect(url_for("get_categories"))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


# Delete Category 
@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("get_categories"))


# Change true to false before submitting 


# --------------- Utensils

# Credit: code taken from task manager project and adapted to fit utensils section of project.

# Cooking utensils 
@app.route("/utensils")
def utensils():
    utensils = list(mongo.db.utensils.find())
    return render_template("utensils.html", utensils=utensils)


@app.route("/utensil/<utensil_id>")
def utensil(utensil_id):
    utensil = mongo.db.utensils.find_one({"_id": ObjectId(utensil_id)})
    return render_template("utensil.html", utensil=utensil)


# Search for utensils 
@app.route("/search_utensil", methods=["GET", "POST"])
def search_utensil():

    query = request.form.get("query")
    print(query)
    utensils = list(mongo.db.utensils.find({"$text": {"$search": query}}))
    return render_template("utensils.html", utensils=utensils)


# Add Utensil
@app.route("/add_utensil", methods=["GET", "POST"])
def add_utensil():
    if request.method == "POST":
        utensil = {
            "utensil_name": request.form.get("utensil_name"),
            "utensil_description": request.form.get("utensil_description"),
            "utensil_details": request.form.get("utensil_details"),
            "utensil_image": request.form.get("utensil_image"),
            "created_by": session["user"]
        }
        mongo.db.utensils.insert_one(utensil)
        flash("You're utensil was successfully added")
        return redirect(url_for("add_utensil"))

    name = mongo.db.utensils.find().sort("utensil_name", 1)
    return render_template("add_utensil.html", name=name)


# Delete Utensil
@app.route("/delete_utensil/<utensil_id>")
def delete_utensil(utensil_id):
    mongo.db.utensils.remove({"_id": ObjectId(utensil_id)})
    flash("You're utensil has been deleted")
    return redirect(url_for("utensils"))


# Edit Utensil
@app.route("/edit_utensil/<utensil_id>", methods=["GET", "POST"])
def edit_utensil(utensil_id):
    if request.method == "POST":
        submit_utensil = {
            "utensil_name": request.form.get("utensil_name"),
            "utensil_description": request.form.get("utensil_description"),
            "utensil_details": request.form.get("utensil_details"),
            "utensil_image": request.form.get("utensil_image"),
            "created_by": session["user"]
        }
        mongo.db.utensils.update({"_id": ObjectId(utensil_id)}, submit_utensil)
        flash("Utensil was successfully updated")

    utensil = mongo.db.utensils.find_one({"_id": ObjectId(utensil_id)})
    return render_template("edit_utensil.html", utensil=utensil)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)