from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.urls import reverse
from tinymce.models import HTMLField
from django.utils import timezone


# Create your models here.

class Salonas(models.Model):
    pavadinimas = models.CharField(max_length=255)
    miestas = models.CharField(max_length=255, blank=True)
    adresas = models.CharField(max_length=255)
    description = HTMLField(default="Salonas description")
    cover = models.ImageField("Virselis", upload_to="covers", null=True)

    class Meta:
        verbose_name = "Salonas"
        verbose_name_plural = "Salonai"

    def __str__(self):
        return f"{self.pavadinimas} {self.adresas}"


class Paslauga(models.Model):
    title = models.CharField("Pavadinimas", max_length=200)
    summary = models.TextField("Aprašymas", max_length=1000, help_text="Paslaugos aprašymas")
    kaina = models.CharField('Paslaugu kaina', max_length=10)
    cover = models.ImageField("Virselis", upload_to="covers", null=True)
    salono_id = models.ForeignKey(Salonas, on_delete=models.CASCADE, related_name="paslauga_rn")

    class Meta:
        verbose_name = "Paslauga"
        verbose_name_plural = "Paslaugos"

    def get_absolute_url(self):
        return reverse("paslauga_n", args=[str(self.id)])

    def __str__(self):
        return f"{self.title} {self.kaina} {self.salono_id}"


class Specialistas(models.Model):
    vardas = models.CharField(max_length=255)
    pavarde = models.CharField(max_length=255)
    patirtis = models.IntegerField()
    description = HTMLField(default="Apie specialista")
    cover = models.ImageField("Specialisto nuotrauka", upload_to="covers", null=True)
    paslaugos_id = models.ForeignKey(Paslauga, on_delete=models.SET_NULL, related_name="specialistas_rn", null=True,
                                     blank=True)
    klientas = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Specialistas"
        verbose_name_plural = "Specialistai"

    def __str__(self):
        return f"{self.vardas} {self.pavarde}"


class PaslaugosRezervacija(models.Model):
    date_created = models.DateTimeField(default=timezone.now() + timezone.timedelta(hours=3))
    laikas_nuo = models.DateTimeField("Laikas nuo", null=True, blank=True)
    laikas_iki = models.DateTimeField("Laikas iki", null=True, blank=True)
    specialistas_id = models.ForeignKey(Specialistas, related_name='spec_paslaugos_rez_rn', on_delete=models.CASCADE,
                                        null=True, blank=True)
    paslaugos_id = models.ForeignKey(Paslauga, on_delete=models.CASCADE, null=True, blank=True)
    klientas = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Rezervacija'
        verbose_name_plural = 'Rezervacijos'
        ordering = ['date_created']

    def __str__(self):
        return f'{self.date_created} {self.paslaugos_id} {self.specialistas_id} {self.klientas}'


class SpecialistoReview(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    content = models.TextField("Atsiliepimas", max_length=1000)
    specialistas_id = models.ForeignKey(Specialistas, on_delete=models.CASCADE, null=True, blank=True)
    klientas = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Atsiliepimas'
        verbose_name_plural = 'Atsiliepimai'
        ordering = ['date_created']


class Profilis(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nuotrauka = models.ImageField(default='profile_pics/default.png', upload_to="profile_pics")

    def __str__(self):
        return f"{self.user.username} profilis"

    def save(self, *args,
             **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.nuotrauka.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.nuotrauka.path)
        elif img.height < 300 or img.width < 300:
            output_size = (300, 300)
            resized_img = img.resize(output_size)
            resized_img.save(self.nuotrauka.path)
