from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Person


@receiver(post_save, sender=Person)
def person_modified(sender, instance, created, **kwargs):
    if not created:
        try:
            user = User.objects.get(person=instance)
        except:
            pass
        else:
            user.first_name = instance.first_name
            user.last_name = instance.last_name
            user.email = instance.email
            user.username = instance.username
            user.save()