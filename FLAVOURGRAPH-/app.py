import json
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'secret_key_here'

with open('recipes.json', 'r') as f:
    recipes_data = json.load(f)

def find_matching_recipes(user_ingredients, max_results=5):
    user_set = set([i.strip().lower() for i in user_ingredients])
    matched = []
    for recipe in recipes_data:
        recipe_ingredients = set([x["name"].lower() for x in recipe["ingredient_details"]])
        common = user_set & recipe_ingredients
        if common:
            matched.append((len(common), recipe))
    matched.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in matched[:max_results]]

@app.route('/', methods=['GET'])
def home():
    saved = session.get('saved_recipes', [])
    return render_template('index.html', saved_recipes=saved, recipes_data=recipes_data)

@app.route('/suggest-recipes', methods=['POST'])
def suggest_recipes():
    ingredients = request.form.get('ingredients', '')
    user_ingredients = [i.strip() for i in ingredients.split(",") if i.strip()]
    matched_recipes = find_matching_recipes(user_ingredients)
    return render_template('results.html', suggestions=matched_recipes, user_ingredients=ingredients)

@app.route('/recipe/<name>', methods=['GET'])
def recipe_detail(name):
    recipe = next((r for r in recipes_data if r["name"] == name), None)
    if not recipe:
        return "Recipe not found", 404
    return render_template('preparation.html', recipe=recipe)

@app.route('/save-recipe', methods=['POST'])
def save_recipe():
    recipe_name = request.form.get('recipe_name')
    if not recipe_name:
        return redirect(url_for('home'))
    saved = session.get('saved_recipes', [])
    if recipe_name not in saved:
        saved.append(recipe_name)
    session['saved_recipes'] = saved
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
