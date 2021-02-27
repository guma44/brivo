import pytest

pytestmark = pytest.mark.django_db


import os
import re
import json

from django.db import connections
from django.db.utils import OperationalError
from django.core.management import BaseCommand

from brivo.brew import models
from brivo.users.models import User
from brivo.utils.measures import BeerColor, BeerGravity
from measurement.measures import Volume, Weight, Temperature

root = os.path.join(os.path.dirname(os.path.abspath(__file__)))

_FLOAT_REGEX = re.compile(r"^-?(?:\d+())?(?:\.\d*())?(?:e-?\d+())?(?:\2|\1\3)$")
_INT_REGEX = re.compile(r"^(?<![\d.])[0-9]+(?![\d.])$")
_EMAIL_REGEX = re.compile(r"(.+@[a-zA-Z0-9\.]+,?){1,}")


def _convert_type(data):
    """Check and convert the type of variable"""

    if _FLOAT_REGEX.match(data) is not None:  # Floats
        return float(data)
    elif _INT_REGEX.match(data) is not None:  # Integers
        return int(data)
    elif data == "True" or data == "true":
        return True
    elif data == "False" or data == "false":
        return False
    else:
        return str(data)  # The rest is string

def _clean_data(data):
    new_data = {}
    for k, v in data.items():
        if v == "" or v == "-":
            continue
        new_data[k] = _convert_type(str(v))
    return new_data


def load_user():
    user = User(email="test@email.com", username="test", password="testpass123")
    user.save()
    print(user)
    return user

def load_styles():
    with open(os.path.join(root, "../management/commands/data/styles.json")) as fin:
        styles = json.load(fin)
        i = 0
        for kwargs in styles:
            kwargs = _clean_data(kwargs)
            # print(str(kwargs))
            for grv in ["og_min", "og_max", "fg_min", "fg_max"]:
                if kwargs.get(grv):
                    kwargs[grv] = BeerGravity(sg=kwargs[grv])
            for clr in ["color_min", "color_max"]:
                if kwargs.get(clr):
                    kwargs[clr] = BeerColor(srm=kwargs[clr])
            if not models.Style.objects.filter(name=kwargs["name"]).count():
                tags = None
                if kwargs.get("tags"):
                    tags = [models.Tag(name=s.strip()) for s in kwargs.get("tags", "").split(",")]
                    for t in tags:
                        t.save()
                    del kwargs["tags"]
                style = models.Style(**kwargs)
                style.save()
                if tags is not None:
                    style.tags.set(tags)
                style.save()
                i += 1
        print((f"Successfully loaded {i} styles to DB"))

def get_recipes_json():
    with open(os.path.join(root, "recipes.json")) as fin:
        recipes = json.load(fin)
    return recipes
        

def load_recipes(user):
    recipes = get_recipes_json()
    recipes_objects = []
    for recipe in recipes:
        recipe_data = _clean_data(recipe["fields"])
        style = models.Style.objects.filter(name__icontains=recipe_data["style"])
        recipe_data["user"] = user
        if style.count() == 0:
            print(f"Did not fount a syle '{recipe_data['style']}' for '{recipe_data['name']}'")
        recipe_data["style"] = style[0]
        recipe_data["expected_beer_volume"] = Volume(
            **{recipe_data["expected_beer_volume"].split()[-1].split("(")[0]: float(recipe_data["expected_beer_volume"].split()[0])})
        # print(recipe_data)
        new_recipe = models.Recipe(**recipe_data)
        new_recipe.save()
        fermentables = []
        for fermentable in recipe["fermentables"]:
            data = _clean_data(fermentable)
            data["recipe"] = new_recipe
            data["amount"] = Weight(**{data["unit"]: data["amount"]})
            data["color"] = BeerColor(ebc=data["color"])
            del data["unit"]
            fermentable_ingredient = models.FermentableIngredient(**data)
            fermentable_ingredient.save()
            fermentables.append(fermentables)
        hops = []
        for hop in recipe["hops"]:
            data = _clean_data(hop)
            data["recipe"] = new_recipe
            data["amount"] = Weight(**{data["unit"]: data["amount"]})
            del data["unit"]
            data["time_unit"] = data["time_unit"].split("(")[0]
            hop_ingredient = models.HopIngredient(**data)
            hop_ingredient.save()
            hops.append(hops)
        yeasts = []
        for yeast in recipe["yeasts"]:
            data = _clean_data(yeast)
            data["recipe"] = new_recipe
            data["amount"] = Weight(**{data["unit"]: data["amount"]})
            del data["unit"]
            yeast_ingredient = models.YeastIngredient(**data)
            yeast_ingredient.save()
            yeasts.append(yeasts)
        extras = []
        for extra in recipe["extras"]:
            data = _clean_data(extra)
            data["recipe"] = new_recipe
            data["amount"] = Weight(**{data["unit"]: data["amount"]})
            del data["unit"]
            data["time_unit"] = data["time_unit"].split("(")[0]
            extra_ingredient = models.ExtraIngredient(**data)
            extra_ingredient.save()
            extras.append(extras)
        mash_steps = []
        for mash in recipe["mashing"]:
            data = _clean_data(mash)
            data["recipe"] = new_recipe
            data["temperature"] = Temperature(c=data["temp"])
            del data["temp"]
            del data["time_unit"]
            mash_step = models.MashStep(**data)
            mash_step.save()
            mash_steps.append(mash_step)
        new_recipe.save()
        recipes_objects.append((recipe, new_recipe))
    return recipes_objects
    


def test_recipe():
    original_recipe = get_recipes_json()[0]
    user = load_user()
    styles = load_styles()
    recipes = load_recipes(user)
    i = 1
    dat = []
    for original_recipe, recipe in recipes:
        diff = recipe.get_gravity().plato - float(original_recipe['extra_info']['gravity_blg'])
        mess = f"{i}. Recipe {recipe.name} diff: {diff}, volume {recipe.expected_beer_volume.l}, {recipe.get_gravity().plato} vs. {float(original_recipe['extra_info']['gravity_blg'])}"
        dat.append((diff, mess))
        print(f"{i}. Recipe {recipe.name}")
        assert recipe.get_boil_size().l == pytest.approx(float(original_recipe["extra_info"]["boil_size"].split()[0]), rel=1e-1, abs=1e-2),  f"Volume value not equal for {recipe.name}"
        assert recipe.get_gravity().plato == pytest.approx(float(original_recipe["extra_info"]["gravity_blg"]), rel=1e-1, abs=1e-2),  f"Gravity alue not equal for {recipe.name}"
        assert recipe.get_ibu() == pytest.approx(float(original_recipe["extra_info"]["ibu"]), rel=1e-1, abs=1e-2),  f"IBU value not equal for {recipe.name}"
        assert recipe.get_color().srm == pytest.approx(float(original_recipe["extra_info"]["srm"]), rel=1e-1, abs=1e-2),  f"SRM value not equal for {recipe.name}"
        i += 1
    # dat_sorted = sorted(dat, key=lambda x: x[0])
    # for d in dat_sorted:
    #     print(d[1])
    # assert True