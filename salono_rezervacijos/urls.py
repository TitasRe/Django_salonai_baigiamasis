from django.urls import path, include
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.index, name='index_name'),
    path('salonai/', views.salonai, name='salonai_n'),
    path('salonai/<int:salonas_id>', views.salonas, name='salonas_n'),
    path("specialistai/", views.SpecialistaiListView.as_view(), name='specialistai_n'),
    path("specialistai/<int:pk>", views.SpecialistasDetailView.as_view(), name='specialistas-detail_n'),
    path("paslaugos/", views.PaslaugosListView.as_view(), name='paslaugos_n'),
    path("paslaugos/<int:pk>", views.PaslaugoaDetailView.as_view(), name='paslauga-detail_n'),
    path('mano_uzsakymai/', views.UserReservations.as_view(), name='mano_uzsakymai_n'),
    path('mano_uzsakymai/<int:pk>/delete', views.UzsakymasByUserDeleteView.as_view(),
         name='mano-uzsakymas-delete_n'),
    path("search/", views.search, name='search_n'),
    path('profilis/', views.profilis, name='profilis_n'),

]

urlpatterns = urlpatterns + [
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", views.register, name='register_n'),

]
