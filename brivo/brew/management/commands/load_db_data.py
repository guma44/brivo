import os
import re
import json

from django.db import connections
from django.db.utils import OperationalError
from django.core.management import BaseCommand

from brivo.brew import models
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


class Command(BaseCommand):
    """Django command to load initiall data to DB"""

    def handle(self, *args, **options):
        self.stdout.write("Loading Countries to DB")
        with open(os.path.join(root, "data/countries.json")) as fin:
            countries = json.load(fin)
            i = 0
            for kwargs in countries:
                if not models.Country.objects.filter(code=kwargs["code"]).count():
                    country = models.Country(**kwargs)
                    country.save()
                    i += 1
                else:
                    self.stdout.write(self.style.WARNING(f"Country {kwargs['code']} already in DB"))
            self.stdout.write(self.style.SUCCESS(f"Successfully loaded {i} countries to DB"))
        self.stdout.write("Loading Fermentable to DB")
        with open(os.path.join(root, "data/fermentables.json")) as fin:
            fermentables = json.load(fin)
            i = 0
            for kwargs in fermentables:
                kwargs = _clean_data(kwargs)
                # self.stdout.write(str(kwargs))
                if kwargs.get("country"):
                    try:
                        kwargs["country"] = models.Country.objects.get(code=kwargs.get("country"))
                    except Exception as err:
                        if kwargs.get("country", ""):
                            raise
                        self.stdout.write(self.style.WARNING(f"Fermentable {kwargs['name']} has no country"))
                        del kwargs["country"]
                # if not models.Fermentable.objects.filter(name=kwargs["name"]).count():
                for clr in ["color"]:
                    if kwargs.get(clr):
                        kwargs[clr] = BeerColor(srm=kwargs[clr])
                fermentable = models.Fermentable(**kwargs)
                fermentable.save()
                i += 1
                # self.stdout.write(self.style.WARNING(f"Fermentable {kwargs['name']} already in DB"))
            self.stdout.write(self.style.SUCCESS(f"Successfully loaded {i} fermentables to DB"))

        with open(os.path.join(root, "data/styles.json")) as fin:
            styles = json.load(fin)
            i = 0
            for kwargs in styles:
                kwargs = _clean_data(kwargs)
                # self.stdout.write(str(kwargs))
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
            self.stdout.write(self.style.SUCCESS(f"Successfully loaded {i} styles to DB"))

        with open(os.path.join(root, "data/hops.json")) as fin:
            hops_substitutes = {}
            hops = json.load(fin)
            i = 0
            for kwargs in hops:
                kwargs = _clean_data(kwargs)
                # self.stdout.write(str(kwargs))
                if kwargs.get("country"):
                    try:
                        kwargs["country"] = models.Country.objects.get(name=kwargs.get("country"))
                    except Exception as err:
                        if kwargs.get("country", ""):
                            raise
                        self.stdout.write(self.style.WARNING(f"Hop {kwargs['name']} has no country"))
                        del kwargs["country"]
                if not models.Hop.objects.filter(name=kwargs["name"]).count():
                    if kwargs.get("substitute"):
                        substitute = [s.strip() for s in kwargs.get("substitute", "").split(",")]
                        del kwargs["substitute"]
                    kwargs["alpha_acids"] = (kwargs["alpha_max"] + kwargs["alpha_min"]) / 2.0
                    hop = models.Hop(**kwargs)
                    hop.save()
                    if len(substitute) > 0:
                        hops_substitutes[hop.id] = substitute
                    i += 1
            for pk, subs in hops_substitutes.items():
                hop = models.Hop.objects.get(pk=pk)
                hop_subs = models.Hop.objects.filter(name__in=subs)
                if hop_subs.count() != len(subs):
                    not_found = set(subs) - set([h.name for h in hop_subs])
                    self.stdout.write(f"TODO: Could not find all substitue Hops: {pk}, {subs}, {not_found}")
                hop.substitute.set(hop_subs)
                # self.stdout.write(self.style.WARNING(f"Hop {kwargs['name']} already in DB"))
            self.stdout.write(self.style.SUCCESS(f"Successfully loaded {i} hops to DB"))

        with open(os.path.join(root, "data/yeasts.json")) as fin:
            # yeasts_styles = {}
            yeasts = json.load(fin)
            i = 0
            for kwargs in yeasts:
                kwargs = _clean_data(kwargs)
                for temp in ["temp_min", "temp_max"]:
                    if kwargs.get(temp):
                        kwargs[temp] = Temperature(celsius=kwargs[temp])
                if not models.Yeast.objects.filter(name=kwargs["name"]).count():
                    # if kwargs.get("styles"):
                    #     styles = [s.strip().rstrip("s") for s in kwargs.get("styles", "").split(",")]
                    #     del kwargs["styles"]
                    yeast = models.Yeast(**kwargs)
                    yeast.save()
                    # if len(styles) > 0:
                    #     yeasts_styles[yeast.id] = styles
                    i += 1
            # for pk, stls in yeasts_styles.items():
            #     yeast = models.Yeast.objects.get(pk=pk)
            #     yeast_stls = models.Style.objects.filter(name__in=stls)
            #     if yeast_stls.count() != len(stls):
            #         not_found = set(stls) - set([h.name for h in yeast_stls])
            #         self.stdout.write(f"TODO: Could not find all styles for Yeasts: {pk}, {stls}, {not_found}")
            #     yeast.styles.set(yeast_stls)
                # self.stdout.write(self.style.WARNING(f"Yeast {kwargs['name']} already in DB"))
            self.stdout.write(self.style.SUCCESS(f"Successfully loaded {i} yeasts to DB"))

        with open(os.path.join(root, "data/extras.json")) as fin:
            extras = json.load(fin)
            i = 0
            for kwargs in extras:
                kwargs = _clean_data(kwargs)
                if not models.Extra.objects.filter(name=kwargs["name"]).count():
                    extra = models.Extra(**kwargs)
                    extra.save()
                    i += 1
            self.stdout.write(self.style.SUCCESS(f"Successfully loaded {i} extras to DB"))
