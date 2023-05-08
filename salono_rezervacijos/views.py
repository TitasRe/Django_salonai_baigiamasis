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
    """
    Atvaizduoja kiek salonu yra bei specialistu ir kiek kartu,
    vartotojas apsilankė puslapį
    """
    num_salonai = Salonas.objects.all().count()
    num_specialistai = Specialistas.objects.all().count()
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    data = {
        'num_salonai_cntx': num_salonai,
        'num_specialistai_cntx': num_specialistai,
        'num_visits_cntx': num_visits
    }

    return render(request, 'index.html', context=data)


def salonai(request):
    """
    Atvaizduoja visus salonus ir juos supuslapiuoja
    """
    paginator = Paginator(Salonas.objects.all(), 3)
    page_number = request.GET.get('page')
    paged_salonai = paginator.get_page(page_number)

    data = {
        'salonai_cntx': paged_salonai
    }
    return render(request, 'salonai.html', context=data)


def salonas(requst, salonas_id):
    """
    Atvaizduoja viena konkretu salona
    """
    salonas = get_object_or_404(Salonas, pk=salonas_id)
    data = {
        'salonas_cntx': salonas
    }
    return render(requst, 'salonas.html', context=data)


class PaslaugosListView(generic.ListView):
    """
    Atvaizduoja visas atliekamas paslauga ir supuslapiuoja
    """
    model = Paslauga
    paginate_by = 5
    context_object_name = 'paslaugos_list'
    template_name = "paslaugos_list.html"


class PaslaugoaDetailView(generic.edit.FormMixin, generic.DetailView):
    """
    Paslaugos detalus view kuriame implementuota paslaugos uzsakymo forma
    su pasirinkimais datos ir laiko. Norima paslaugos rezervacija patikrinama butent
    su tais kurie specialistai atlieka sia paslauga ir ar ju esamos rezervacijos nesikerta su norima rezervacija,
    dar pridėjau artimiausia laiką
    """
    model = Paslauga
    context_object_name = 'paslauga'
    template_name = 'paslauga_detail.html'
    form_class = PaslaugosRezervacijaForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservations = PaslaugosRezervacija.objects.filter(paslaugos_id=self.object)
        specialistai = Specialistas.objects.filter(paslaugos_id=self.object)

        now = datetime.now()
        time_list = []

        for specialistas_obj in specialistai:
            start_time = datetime.combine(datetime.today(), datetime.strptime('08:00', '%H:%M').time())
            end_time = datetime.combine(datetime.today(), datetime.strptime('18:00', '%H:%M').time())
            while start_time <= end_time:
                if start_time >= now:
                    time_list.append(start_time.strftime('%Y-%m-%d %H:%M:%S'))
                start_time += timedelta(hours=1)

        for rezervacijos_obj in reservations: #jei yra ismetu
            rezervacijos_time_str = rezervacijos_obj.laikas_nuo.strftime('%Y-%m-%d %H:%M:%S')
            if rezervacijos_time_str in time_list:
                time_list.remove(rezervacijos_time_str)

        if not time_list:
            time_list.append("Šiandien laisvų laikų neturime")

        context['laisvi_laikai'] = min(time_list)
        return context

    # sekmes atvieju nuves cia
    def get_success_url(self):
        return reverse('paslauga-detail_n', kwargs={'pk': self.object.id})

    # tikrinu ar forma validi ar ne
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
        laikas_nuo = form.cleaned_data['laikas_nuo']
        dirbam_nuo = time(8, 0, 0)
        dirbam_iki = time(18, 0, 0)
        if laikas_nuo.time() > dirbam_iki or laikas_nuo.time() < dirbam_nuo:
            messages.error(self.request, f'Salonas dirba nuo 8:00 iki 19:00')
            return redirect(reverse('paslauga-detail_n', kwargs={'pk': self.object.id}))
        if laikas_nuo.date().weekday() in [5, 6]:
            messages.error(self.request, f'Salonas nedirba savaitgaliais')
            return redirect(reverse('paslauga-detail_n', kwargs={'pk': self.object.id}))
        # pasiemu visus specialistus kurie atlieka sia paslauga!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        visi_paslaugos_specialistai = Specialistas.objects.filter(paslaugos_id=paslauga)
        if len(visi_paslaugos_specialistai) < 1:
            messages.error(self.request, f'Specialistų teikiančią šią paslaugą šiuo metu neturime')
            return redirect(reverse('paslauga-detail_n', kwargs={'pk': self.object.id}))
        listas_specialistu_kurieturirezervacijas_netinka = []
        listas_specialistu_kurie_turi_laisvu_laiku_kada_zmogus_iesko = []
        listas_specialistu_kurie_is_vis_neturi_jokiu_rezervaciju = []
        if laikas_nuo - timedelta(hours=3, minutes=1) < timezone.localtime():
            messages.error(self.request, f'Negalite užsisakyti paslaugų į praeitį')
            return redirect(reverse('paslauga-detail_n', kwargs={'pk': self.object.id}))
        # kad visos paslaugos trunka 59 min
        form.instance.laikas_iki = laikas_nuo + timedelta(minutes=59)
        for paslaugos_specialistas in visi_paslaugos_specialistai:  # visi spec kurie atlieka ta paslauga
            if paslaugos_specialistas.spec_paslaugos_rez_rn.all():  # tikrinu specialisto rezervacija
                for paslaugos_rezervacija in paslaugos_specialistas.spec_paslaugos_rez_rn.all():
                    # arba pries arba po rezervacijos
                    if laikas_nuo > paslaugos_rezervacija.laikas_iki or laikas_nuo + timedelta(
                            minutes=59) < paslaugos_rezervacija.laikas_nuo:
                        listas_specialistu_kurie_turi_laisvu_laiku_kada_zmogus_iesko.append(paslaugos_specialistas)
                    else:
                        listas_specialistu_kurieturirezervacijas_netinka.append(paslaugos_specialistas)
            else:
                listas_specialistu_kurie_is_vis_neturi_jokiu_rezervaciju.append(
                    paslaugos_specialistas)  # pridedu specialistus kurie neturi rezervaciju
        if len(listas_specialistu_kurie_is_vis_neturi_jokiu_rezervaciju) >= 1:
            paslaugos_specialistas = listas_specialistu_kurie_is_vis_neturi_jokiu_rezervaciju[
                0]  # tas ir bus specialistas
        else:
            pasl_specialistai_laisvi = []
            for item in listas_specialistu_kurie_turi_laisvu_laiku_kada_zmogus_iesko:
                if item not in listas_specialistu_kurieturirezervacijas_netinka:
                    pasl_specialistai_laisvi.append(item)
            if len(pasl_specialistai_laisvi) < 1:
                messages.error(self.request, f'Laisvų specialistų pasirinktu laiku nėra!')
                return redirect(reverse('paslauga-detail_n', kwargs={'pk': self.object.id}))
            paslaugos_specialistas = pasl_specialistai_laisvi[0]

        if laikas_nuo.date() < timezone.localdate():  # patikrinu ar nera praeities data
            messages.error(self.request, f'Pasirinktas laikas atbuline data negalimas ')
            return redirect(reverse('paslauga-detail_n', kwargs={'pk': self.object.id}))

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
    """
    Konkretaus vartotojo uzsakymai, kuris yra prisijunges
    Ir yra rikiuojamos pagal laika
    """
    model = PaslaugosRezervacija
    template_name = 'kliento_uzsakymai.html'
    context_object_name = 'kliento_uzsakymu_list'  # šiaip sugeneruoja automatiškai bet galim patys pasivadinti kaip norim
    paginate_by = 10

    def get_queryset(self):
        query = PaslaugosRezervacija.objects.filter(klientas=self.request.user).order_by('laikas_nuo')
        return query


class UzsakymasByUserDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    """
    Leidzia varotojui istrinti uzsakyma
    Bei patikrina ar tikrai tas vartotojas
    """
    model = PaslaugosRezervacija
    success_url = "/salono_rezervacijos/mano_uzsakymai"
    template_name = "kliento_uzsakymas_delete.html"

    def test_func(self):
        uzsakymasinstance = self.get_object()
        return self.request.user == uzsakymasinstance.klientas


class SpecialistaiListView(generic.ListView):
    """
    Visu specialistu atvaizdavimas
    """
    model = Specialistas
    paginate_by = 4
    context_object_name = 'specialistai_list'
    template_name = "specialistai_list.html"


class SpecialistasDetailView(generic.edit.FormMixin, generic.DetailView):
    """
    Atvaziduoja konkretu specialista ir yra atsiliepimo forma
    """
    model = Specialistas
    context_object_name = 'specialistas'
    template_name = 'specialistas_detail.html'
    form_class = SpecialistasReviewForm

    def get_success_url(self):
        return reverse('specialistas-detail_n', kwargs={'pk': self.object.id})

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
        messages.info(self.request, f'Atsiliepimas sekmingai paskelbtas!')
        return super().form_valid(form)


def search(request):
    """
    Pagal ka vartotojas gales ieskoti
    """
    query_text = request.GET['search_text']
    query_result2 = Specialistas.objects.filter(paslaugos_id__title__icontains=query_text)
    query_result_paslaugos_specialistai = Specialistas.objects.filter(paslaugos_id__title__icontains=query_text)
    query_result = Salonas.objects.filter(
        Q(pavadinimas__icontains=query_text) |
        Q(miestas__icontains=query_text)
        # Q(paslauga_rn__title__icontains=query_text) |
        # Q(paslauga_rn__specialistas_rn__vardas__icontains=query_text) |
        # Q(paslauga_rn__specialistas_rn__pavarde__icontains=query_text) |
        # Q(paslauga_rn__specialistas_rn__vardas__icontains=query_text) |
        # Q(paslauga_rn__specialistas_rn__pavarde__icontains=query_text))
    )
    data = {
        'query_text_cntx': query_text,
        'query_result_cntx': query_result,
        'query_result_paslauga': query_result2,
        'query_result_paslaugos_specialistai': query_result_paslaugos_specialistai,

    }
    return render(request, "search.html", context=data)


@csrf_protect
def register(request):
    """
    Apdoroja registracijos forma
    """
    if request.method == 'POST':
        vartotojas = request.POST['username']
        emailas = request.POST['email']
        passwordas = request.POST['password']
        passwordas2 = request.POST['password2']
        if passwordas == passwordas2 and len(passwordas) >= 6:
            if User.objects.filter(username=vartotojas).exists():
                messages.error(request, f'Vartotojo vardas {vartotojas} jau egzistuoja')
                return redirect('register_n')
            else:
                if User.objects.filter(email=emailas).exists():
                    messages.error(request, f"Toks emailas: {emailas} jau egzistuoja")
                    return redirect('register_n')
                else:
                    User.objects.create_user(username=vartotojas, email=emailas, password=passwordas)
                    messages.info(request, f"Vartotojas {vartotojas} sukurtas sėkmingai")
                    messages.info(request, f"Vartotojas su email: {emailas} sukurtas sėkmingai")
                    return redirect('login')
        else:
            messages.error(request, f'Nesutampa slaptažodžiai')
            return redirect('register_n')

    return render(request, 'registration/register.html')


@login_required
def profilis(request):
    """
    Profilio sukurimui ir atnaujinimui.
    """
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
