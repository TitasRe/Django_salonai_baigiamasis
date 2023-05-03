# suformuojam pati signala
from django.db.models.signals import post_save  # signalas
from django.dispatch import receiver  # gavejo dekoratorius
from django.contrib.auth.models import User  # siuntejas
from .models import Profilis


@receiver(post_save, sender=User)  # po sava priima is USER
# created reiskia kad kuriamas o ne save'vinamas
def create_profile(sender, instance, created, **kwargs):  # jeigu atsitinka toks signalas sukuriama profili useriui
    if created:  # ar ivyko profilio sukurimas
        Profilis.objects.create(user=instance)  # sukuriam pati profili useriui
    else:
        instance.profilis.save()  # per istance paimam esama objekta ir issaugom
    print('printas is signals gavejo, kwargs', kwargs)
