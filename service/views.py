from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from service.forms import ClientForm, MessageForm, MailingForm
from service.models import Client, Mailing, Message
from django.views.generic import (
    TemplateView,
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
)

from service.services import send_mailing


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
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
    form_class = ClientForm
    template_name = "client_form.html"
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
        ).count()

        context["total_clients"] = Client.objects.count()

        return context

class MessageListView(ListView):
    model = Message
    template_name = "messages_list.html"
    context_object_name = "messages_list"


# Создание сообщения
class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "message_form.html"
    success_url = reverse_lazy("service:messages_list")


# Просмотр сообщения
class MessageDetailView(DetailView):
    model = Message
    template_name = "message_detail.html"
    pk_url_kwarg = "message_id"


# Редактирование сообщения
class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "message_form.html"
    pk_url_kwarg = "message_id"

    def get_success_url(self):
        return reverse_lazy(
            "service:message_detail",
            kwargs={"message_id": self.object.pk},
        )


# Удаление сообщения
class MessageDeleteView(DeleteView):
    model = Message
    template_name = "message_confirm_delete.html"
    pk_url_kwarg = "message_id"
    success_url = reverse_lazy("service:messages_list")


@login_required
@require_POST
def mailing_send_view(request, mailing_id):
    mailing = get_object_or_404(Mailing, pk=mailing_id)

    try:
        results = send_mailing(mailing)

        successful = sum(
            1 for result in results
            if result["status"] == "Успешно"
        )

        unsuccessful = len(results) - successful

        messages.success(
            request,
            f"Рассылка завершена. "
            f"Успешно отправлено: {successful}. "
            f"Не успешно: {unsuccessful}."
        )

    except ValueError as error:
        messages.error(request, str(error))

    return redirect(
        "service:mailing_detail",
        mailing_id=mailing.pk,
    )

class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing_form.html"
    success_url = reverse_lazy("service:mailings_list")


class MailingListView(ListView):
    model = Mailing
    template_name = "mailings_list.html"
    context_object_name = "mailings"


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing_form.html"
    pk_url_kwarg = "mailing_id"

    def get_success_url(self):
        return reverse_lazy(
            "service:mailing_detail",
            kwargs={"mailing_id": self.object.pk},
        )


class MailingDetailView(DetailView):
    model = Mailing
    template_name = "mailing_detail.html"
    pk_url_kwarg = "mailing_id"


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = "mailing_confirm_delete.html"
    pk_url_kwarg = "mailing_id"
    success_url = reverse_lazy("service:mailings_list")


class ContactsView(TemplateView):
    template_name = "contacts.html"