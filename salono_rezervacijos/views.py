from django.shortcuts import render
from .models import Salonas, Specialistas, Paslauga, PaslaugosRezervacija
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from .forms import UserUpdateForm, ProfilisUpdateForm, SpecialistasReviewForm, PaslaugosRezervacijaForm
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.utils import timezone
from datetime import datetime, timedelta, time


# Create your views here.
def index(request):
    # suskaičiuojam eilutes kiekvienoje lentelėje
    num_salonai = Salonas.objects.all().count()
    num_specialistai = Specialistas.objects.all().count()
    # issikvieciam sesijos objekta ir prirasom jam apsilankymus
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    data = {
        'num_salonai_cntx': num_salonai,
        'num_specialistai_cntx': num_specialistai,
        'num_visits_cntx': num_visits
    }

    return render(request, 'index.html', context=data)


def salonai(request):
    paginator = Paginator(Salonas.objects.all(), 3)
    page_number = request.GET.get('page')
    paged_salonai = paginator.get_page(page_number)

    data = {
        'salonai_cntx': paged_salonai
    }
    return render(request, 'salonai.html', context=data)


def salonas(requst, salonas_id):
    salonas = get_object_or_404(Salonas, pk=salonas_id)
    data = {
        'salonas_cntx': salonas
    }
    return render(requst, 'salonas.html', context=data)


class PaslaugosListView(generic.ListView):
    model = Paslauga
    paginate_by = 5
    context_object_name = 'paslaugos_list'
    template_name = "paslaugos_list.html"


class PaslaugoaDetailView(generic.edit.FormMixin, generic.DetailView):
    model = Paslauga
    context_object_name = 'paslauga'
    template_name = 'paslauga_detail.html'
    form_class = PaslaugosRezervacijaForm
    # sekmes atvieju nuves cia
    def get_success_url(self):
        return reverse('paslauga-detail_n', kwargs={'pk': self.object.id})
    #tikrinu ar forma validi ar ne
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        print(form.errors)
        if form.is_valid():
            print(form.errors)
            return self.form_valid(form)
        else:
            print(form.errors)
            return self.form_invalid(form)

    def form_valid(self, form):
        paslauga = self.object
        #pasiemu tiksliai is laukio laikas_nuo tai ka user pasirinks
        # date_nuo = form.cleaned_data['date_nuo']
        laikas_nuo = form.cleaned_data['laikas_nuo']
        # print("KKKKKKKKKKKKKKKKKKKKKKKKKKK")
        # print(laikas_nuo)
        dirbam_nuo = time(8, 0, 0)
        dirbam_iki = time(17, 0, 0)
        if laikas_nuo.time() > dirbam_iki or laikas_nuo.time() < dirbam_nuo:
            messages.error(self.request, f'Salonas dirba nuo 8:00 iki 17:00')
            return redirect(reverse('paslauga-detail_n', kwargs={'pk': self.object.id}))
        # print(timezone.localtime() + timedelta(hours=3), "Dabartinis laikas")
        # print(paslauga)
        #pasiemu visus specialistus kurie atlieka sia paslauga!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        visi_paslaugos_specialistai = Specialistas.objects.filter(paslaugos_id=paslauga)  # .filter(status='g')
        # print(visi_paslaugos_specialistai)
        #patikrinu ar yra specialistu kurie atlieka sia paslauga
        if len(visi_paslaugos_specialistai) < 1:
            messages.error(self.request, f'Specialistų teikiančią šią paslaugą šiuo metu neturime')
            return redirect(reverse('paslauga-detail_n', kwargs={'pk': self.object.id}))
        listas_specialistu_kurieturirezervacijas_netinka = []
        listas_specialistu_kurie_turi_laisvu_laiku_kada_zmogus_iesko = []
        listas_specialistu_kurie_is_vis_neturi_jokiu_rezervaciju = []
        # print("Laikas nuo + 1")
        # print(laikas_nuo - timedelta(hours=3))
        if laikas_nuo - timedelta(hours=3, minutes=1) < timezone.localtime():
            # print(timezone.localtime())
            messages.error(self.request, f'Negalite užsisakyti paslaugų į praeitį')
            return redirect(reverse('paslauga-detail_n', kwargs={'pk': self.object.id}))
        print("!@!!!!!!!!!!!!!!")
        #kad visos paslaugos trunka 59 min
        form.instance.laikas_iki = laikas_nuo + timedelta(minutes=59)
        print("Laikas nuo + 1")
        print(laikas_nuo)
        for paslaugos_specialistas in visi_paslaugos_specialistai:
            if paslaugos_specialistas.spec_paslaugos_rez_rn.all():
                for paslaugos_rezervacija in paslaugos_specialistas.spec_paslaugos_rez_rn.all():
                    print(paslaugos_specialistas)
                    print("PAAASlaugos rezervacija!!!")
                    print(paslaugos_rezervacija.laikas_nuo)
                    if laikas_nuo > paslaugos_rezervacija.laikas_iki or laikas_nuo + timedelta(
                            minutes=59) < paslaugos_rezervacija.laikas_nuo:  # + timedelta(hours=1):
                        print("IFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFAS")
                        print(paslaugos_rezervacija.laikas_iki)
                        print(laikas_nuo)
                        print("--------------------------")
                        listas_specialistu_kurie_turi_laisvu_laiku_kada_zmogus_iesko.append(paslaugos_specialistas)
                    else:
                        listas_specialistu_kurieturirezervacijas_netinka.append(paslaugos_specialistas)
                        print(paslaugos_rezervacija.laikas_nuo.date())
                        print(laikas_nuo.date())
                        print(paslaugos_rezervacija.laikas_nuo, 'paslaugos_rezervacija.laikas_nuo')
                        print(laikas_nuo)
                        print(paslaugos_rezervacija.laikas_iki)
            else:
                listas_specialistu_kurie_is_vis_neturi_jokiu_rezervaciju.append(paslaugos_specialistas) #pridedu specialistus kurie neturi rezervaciju
        print(listas_specialistu_kurieturirezervacijas_netinka)  # listas specialistu kurie rezervuoti butent ta diena kuria nori user
        print(listas_specialistu_kurie_turi_laisvu_laiku_kada_zmogus_iesko)  # listas specialistu kurie  turi laisva laika butent tuo metu kai nori user
        print(listas_specialistu_kurie_is_vis_neturi_jokiu_rezervaciju)  # listas specialistu kurie  is viso neturi jokiu rezervaciju
        if len(listas_specialistu_kurie_is_vis_neturi_jokiu_rezervaciju) >= 1:
            paslaugos_specialistas = listas_specialistu_kurie_is_vis_neturi_jokiu_rezervaciju[0] #tas ir bus specialistas
            print(paslaugos_specialistas)
        else:
            print([item for item in listas_specialistu_kurie_turi_laisvu_laiku_kada_zmogus_iesko if
                   item not in listas_specialistu_kurieturirezervacijas_netinka])  # gaunu rezervacijas kuriu laikai nera uzimti
            pasl_specialistai_laisvi = [item for item in listas_specialistu_kurie_turi_laisvu_laiku_kada_zmogus_iesko if item not in listas_specialistu_kurieturirezervacijas_netinka]
            print(pasl_specialistai_laisvi)
            if len(pasl_specialistai_laisvi) < 1:
                messages.error(self.request, f'Laisvų specialistų pasirinktu laiku nėra!')
                return redirect(reverse('paslauga-detail_n', kwargs={'pk': self.object.id}))
            paslaugos_specialistas = pasl_specialistai_laisvi[0]
        print(paslauga)
        print(type(paslauga))
        #patikrinu ar jau yra rezervaciju
        existing_rezervacijos = PaslaugosRezervacija.objects.filter(
            paslaugos_id=paslauga,
            specialistas_id=paslaugos_specialistas,
            laikas_nuo__lte=laikas_nuo,
            laikas_iki__gte=form.instance.laikas_iki,
        )

        if laikas_nuo.date() < timezone.localdate(): #patikrinu ar nera praeities laikas
            messages.error(self.request, f'Pasirinktas laikas atbuline data negalimas ')
            return redirect(reverse('paslauga-detail_n', kwargs={'pk': self.object.id}))

        if existing_rezervacijos.exists(): #patikrinu ar jau yra uzimtas laikas ir jei yra kad nepriskirtu vel
            messages.error(self.request,
                           f'Laikas {laikas_nuo} užimtas! Bandykite dar kartą')
            return redirect(reverse('paslauga-detail_n', kwargs={'pk': self.object.id}))
        # nurodau koks specialistas kokia paslauga ir t.t
        form.instance.specialistas_id = paslaugos_specialistas
        form.instance.paslaugos_id = paslauga
        form.instance.klientas = self.request.user
        form.instance.laikas_nuo = laikas_nuo
        form.instance.laikas_iki = laikas_nuo + timedelta(minutes=59)
        print(form.instance.paslaugos_id)
        form.save()
        messages.info(self.request, f'Jūsų rezervacija sėkmingai atlikta!')
        return super().form_valid(form)


class UserReservations(LoginRequiredMixin, generic.ListView):
    model = PaslaugosRezervacija
    template_name = 'kliento_uzsakymai.html'
    context_object_name = 'kliento_uzsakymu_list'  #šiaip sugeneruoja automatiškai bet galim patys pasivadinti kaip norim
    paginate_by = 10

    def get_queryset(self):
        query = PaslaugosRezervacija.objects.filter(klientas=self.request.user).order_by('laikas_nuo')
        return query


class UzsakymasByUserDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = PaslaugosRezervacija
    success_url = "/salono_rezervacijos/mano_uzsakymai"
    template_name = "kliento_uzsakymas_delete.html"

    # kad tik tas useris kuris gali prisijunges gali keisti.
    def test_func(self):
        # paiims is view objektą kad galetumem patikrinti
        uzsakymasinstance = self.get_object()
        return self.request.user == uzsakymasinstance.klientas


# class UzsakymasByUserDetailView(LoginRequiredMixin, generic.DetailView):  # per mygtuka
#     model = PaslaugosRezervacija
#     template_name = 'kliento_uzsakymai.html'

class SpecialistaiListView(generic.ListView):  # listview = select all
    model = Specialistas  # is kokio modelio bus formuotojamas view
    paginate_by = 4  # čia kiek matysim vienam puslapi specialistu
    context_object_name = 'specialistai_list'
    template_name = "specialistai_list.html"


class SpecialistasDetailView(generic.edit.FormMixin, generic.DetailView):  # detailview = pagal PK grazina 1 eilute
    model = Specialistas
    context_object_name = 'specialistas'
    template_name = 'specialistas_detail.html'
    form_class = SpecialistasReviewForm

    def get_success_url(self):  # kwargs paduodam i URL PK arba ID
        return reverse('specialistas-detail_n', kwargs={'pk': self.object.id})  # nustatom endoinpta is URLS

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.content = form.cleaned_data['content']
        form.instance.specialistas_id = self.object
        form.instance.klientas = self.request.user

        form.save()
        messages.info(self.request, f'Atsiliepimas sekmingai paskelbtas! :)')
        return super().form_valid(form)


def search(request):
    query_text = request.GET['search_text']
    query_result = Salonas.objects.filter(
        Q(pavadinimas__icontains=query_text) |
        Q(miestas__icontains=query_text) |
        Q(paslauga_rn__title__icontains=query_text) |
        Q(paslauga_rn__specialistas_rn__vardas__icontains=query_text) |
        Q(paslauga_rn__specialistas_rn__pavarde__icontains=query_text))
    data = {
        'query_text_cntx': query_text,
        'query_result_cntx': query_result,
    }
    return render(request, "search.html", context=data)


@csrf_protect  # butinai kad veiktu su browser
def register(request):
    # tikrininam ar GET ar POST metodas
    if request.method == 'POST':
        vartotojas = request.POST['username']
        emailas = request.POST['email']
        passwordas = request.POST['password']
        passwordas2 = request.POST['password2']
        # tikrinam ar sutampa slaptažodis
        if passwordas == passwordas2 and len(passwordas) >= 6:
            # tikrinam ar vartotojas jau egzistuoja
            if User.objects.filter(username=vartotojas).exists():  # gražina true arba false
                # Jeigu user jau egzistuoja siunčiam šia žinute
                messages.error(request, f'Vartotojo vardas {vartotojas} jau egzistuoja')
                # Ir forma paduodam iš naujo
                return redirect('register_n')
            else:  # Tikrinam email
                if User.objects.filter(email=emailas).exists():
                    messages.error(request, f"Toks emailas: {emailas} jau egzistuoja")
                    return redirect('register_n')
                else:  # tada tiesiog sukuriam nauja vartotoja
                    User.objects.create_user(username=vartotojas, email=emailas, password=passwordas)
                    messages.info(request, f"Vartotojas {vartotojas} sukurtas sėkmingai")
                    messages.info(request, f"Vartotojas su email: {emailas} sukurtas sėkmingai")
                    return redirect('login') #nukreipimas i login puslpai
        else:  # kai slaptazodis nesutampa
            messages.error(request, f'Nesutampa slaptažodžiai')
            # paleidžiam forma iš naujo
            return redirect('register_n')

    # Get rezultatas pries uzpildant forma!
    return render(request, 'registration/register.html')


@login_required
def profilis(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfilisUpdateForm(request.POST, request.FILES,
                                    instance=request.user.profilis)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.info(request, f'Profilis sėkmingai atnaujintas')
            return redirect('profilis_n')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfilisUpdateForm(instance=request.user.profilis)
        data = {
            'u_form_cntx': u_form,
            'p_form_cntx': p_form,
        }
        return render(request, 'profilis.html', context=data)
