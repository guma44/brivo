from django.db import models
from django.db.models.base import ModelBase
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _

from modelcluster.models import ClusterableModel
from slugify import slugify as pyslugify


MASS_UNITS = (
    ('g', 'g'),
    ('kg', 'Kg'),
    ('oz', 'oz'),
    ('lb', 'lb'))

VOLUME_UNITS = (
    ('l', 'l'),
    ('ml', 'ml'),
    ('us_oz', 'us_oz'), ('us_g', 'us_g'))

TIME_CHOICE = [
 ('MINUTE', 'minute'),
 ('HOUR', 'hour'),
 ('DAY', 'day'),
 ('WEEK', 'week'),
 ('MONTH', 'month'),
 ('YEAR', 'year')
 ]



####################################################################################
## From https://github.com/un33k/django-uuslug
def slugify(text, entities=True, decimal=True, hexadecimal=True, max_length=0,
            word_boundary=False, separator='-', save_order=False, stopwords=()):
    """Make a slug from a given text."""

    return smart_str(pyslugify(text, entities, decimal, hexadecimal, max_length,
        word_boundary, separator, save_order, stopwords))


def uuslug(s, instance, entities=True, decimal=True, hexadecimal=True,
           slug_field='slug', filter_dict=None, start_no=1, max_length=0,
           word_boundary=False, separator='-', save_order=False, stopwords=()):
    """ This method tries a little harder than django's django.template.defaultfilters.slugify. """

    if isinstance(instance, ModelBase):
        raise Exception("You must pass an instance to uuslug, not a model.")

    queryset = instance.__class__.objects.all()
    if filter_dict:
        queryset = queryset.filter(**filter_dict)
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # The slug max_length cannot be bigger than the max length of the field
    slug_field_max_length = instance._meta.get_field(slug_field).max_length
    if not max_length or max_length > slug_field_max_length:
        max_length = slug_field_max_length

    slug = slugify(s, entities=entities, decimal=decimal, hexadecimal=hexadecimal,
                   max_length=max_length, word_boundary=word_boundary, separator=separator,
                   save_order=save_order, stopwords=stopwords)

    new_slug = slug
    counter = start_no
    while queryset.filter(**{slug_field: new_slug}).exists():
        if len(slug) + len(separator) + len(str(counter)) > max_length:
            slug = slug[:max_length - len(slug) - len(separator) - len(str(counter))]
        new_slug = "{}{}{}".format(slug, separator, counter)
        counter += 1

    return new_slug
###########################################################################################

class BaseModel(ClusterableModel):
    """Base model for all beer related models"""

    class Meta:
        abstract = True
        app_label = "brewery"

    name = models.CharField(_("Name"), max_length=1000)
    slug = models.SlugField(max_length=1000, blank=True, editable=False)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modified At"), auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuslug(self.name, instance=self)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(BaseModel): pass

class Country(BaseModel):
    code = models.CharField(_("Code"), max_length=1000)

    def __str__(self):
        return f"{self.name} ({self.code})"



