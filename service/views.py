from django.urls import reverse_lazy
from django.utils import timezone

from service.models import Client, Mailing
from django.views.generic import (
    TemplateView,
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
)


class ClientCreateView(CreateView):
    model = Client
    fields = [
        "email",
        "username",
        "comment",
    ]
    template_name = "client_form.html"
    success_url = reverse_lazy("service:clients_list")


class ClientsListView(ListView):
    model = Client
    template_name = "clients_list.html"


class ClientDetailView(DetailView):
    model = Client
    template_name = "client_detail.html"
    pk_url_kwarg = "client_id"


class ClientUpdateView(UpdateView):
    model = Client
    template_name = "client_form.html"
    fields = [
        "email",
        "username",
        "comment",
    ]
    pk_url_kwarg = "client_id"

    def get_success_url(self):
        return reverse_lazy(
            "service:client_detail",
            kwargs={
                "client_id": self.object.pk,
            },
        )


class ClientDeleteView(DeleteView):
    model = Client
    template_name = "client_confirm_delete.html"
    success_url = reverse_lazy("service:client_list")
    pk_url_kwarg = "client_id"


class HomeView(TemplateView):
    template_name = "service/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()

        context["total_mailings"] = Mailing.objects.count()

        context["active_mailings"] = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            status="Запущена",
        ).count()

        context["total_clients"] = Client.objects.count()

        return context
