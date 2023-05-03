from django.contrib import admin
from .models import Profilis, Salonas, Specialistas, Paslauga, PaslaugosRezervacija
# Register your models here.


admin.site.register(Salonas)
admin.site.register(Paslauga)
admin.site.register(Specialistas)
admin.site.register(Profilis)
admin.site.register(PaslaugosRezervacija)