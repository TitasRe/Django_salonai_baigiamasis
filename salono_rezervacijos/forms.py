# importuojam klase kuriai kuriam forma
from .models import Profilis, SpecialistoReview, PaslaugosRezervacija
from django.forms import DateTimeInput

from django.contrib.auth.models import User
from django import forms


class SpecialistasReviewForm(forms.ModelForm):
    class Meta:
        model = SpecialistoReview
        # Nematomi fields bet ju reikia kad galetume suristi ir paimti is views duomenu
        fields = ('content', 'specialistas_id', 'klientas')
        # padarom slaptus
        widgets = {'specialistas_id': forms.HiddenInput(),
                   'klientas': forms.HiddenInput(),
                   }


class PaslaugosRezervacijaForm(forms.ModelForm):
    class Meta:
        model = PaslaugosRezervacija
        fields = ('paslaugos_id', 'klientas', 'specialistas_id', 'laikas_nuo', 'laikas_iki')
        widgets = {
            'paslaugos_id': forms.HiddenInput(),
            'klientas': forms.HiddenInput(),
            'specialistas_id': forms.HiddenInput(),
            'laikas_nuo': DateTimeInput(attrs={'type': 'datetime-local'}),
            'laikas_iki': forms.HiddenInput(),
        }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        # nurodzius modeli surisama su ta klase
        model = User
        fields = ['username', 'email']


#
class ProfilisUpdateForm(forms.ModelForm):
    class Meta:
        model = Profilis
        fields = ['nuotrauka']
