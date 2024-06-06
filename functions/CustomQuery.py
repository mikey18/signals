from django.core.exceptions import ObjectDoesNotExist
# from random import choices


def get_if_exists(Model, **kwargs):
    try:
        obj = Model.objects.get(**kwargs)
    except ObjectDoesNotExist:
        obj = None
    return obj
