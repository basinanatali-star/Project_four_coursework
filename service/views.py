from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Count, Q
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST

from service.forms import ClientForm, MessageForm, MailingForm
from service.models import Client, Mailing, Message, MailingAttempt
from django.views.generic import (
    TemplateView,
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
)

from service.services import send_mailing

def clear_mailings_cache():
    cache.delete_pattern("mailings_list_user_*")

def is_manager(user):
    return user.groups.filter(name="Менеджеры").exists()

User = get_user_model()


@login_required
@user_passes_test(is_manager)
def users_list_view(request):
    users = User.objects.all().order_by("email")

    return render(
        request,
        "service/users_list.html",
        {"users": users},
    )


@login_required
@user_passes_test(is_manager)
@require_POST
def user_block_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if user == request.user:
        messages.error(request, "Нельзя заблокировать самого себя.")

    elif user.is_superuser:
        messages.error(request, "Нельзя заблокировать администратора.")

    else:
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])

        if user.is_active:
            messages.success(request, f"Пользователь {user.email} разблокирован.")
        else:
            messages.success(request, f"Пользователь {user.email} заблокирован.")

    return redirect("service:users_list")


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = "client_form.html"
    success_url = reverse_lazy("service:clients_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientsListView(ListView):
    model = Client
    template_name = "clients_list.html"

    def get_queryset(self):
        if is_manager(self.request.user):
            return Client.objects.all()

        return Client.objects.filter(owner=self.request.user)


class ClientDetailView(DetailView):
    model = Client
    template_name = "client_detail.html"
    pk_url_kwarg = "client_id"

    def get_queryset(self):
        if is_manager(self.request.user):
            return Client.objects.all()

        return Client.objects.filter(owner=self.request.user)


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "client_form.html"
    pk_url_kwarg = "client_id"

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

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
    success_url = reverse_lazy("service:clients_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class HomeView(TemplateView):
    template_name = "service/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for mailing in Mailing.objects.all():
            mailing.update_status()

        now = timezone.now()

        context["total_mailings"] = Mailing.objects.count()

        context["active_mailings"] = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            status="Запущена",
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

        clear_mailings_cache()

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

    def form_valid(self, form):
        form.instance.owner = self.request.user

        response = super().form_valid(form)
        clear_mailings_cache()

        return response

class MailingListView(ListView):
    model = Mailing
    template_name = "mailings_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        user = self.request.user
        cache_key = f"mailings_list_user_{user.pk}"

        mailings = cache.get(cache_key)

        if mailings is not None:
            return mailings

        if is_manager(user):
            queryset = Mailing.objects.all()
        else:
            queryset = Mailing.objects.filter(owner=user)

        mailings = list(
            queryset.select_related("message").prefetch_related("recipients")
        )

        cache.set(cache_key, mailings, 60 * 5)

        return mailings


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing_form.html"
    pk_url_kwarg = "mailing_id"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        clear_mailings_cache()
        return response

    def get_success_url(self):
        return reverse_lazy(
            "service:mailing_detail",
            kwargs={"mailing_id": self.object.pk},
        )

class MailingDetailView(DetailView):
    model = Mailing
    template_name = "mailing_detail.html"
    pk_url_kwarg = "mailing_id"

    def get_queryset(self):
        if is_manager(self.request.user):
            return Mailing.objects.all()

        return Mailing.objects.filter(owner=self.request.user)


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = "mailing_confirm_delete.html"
    pk_url_kwarg = "mailing_id"
    success_url = reverse_lazy("service:mailings_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        clear_mailings_cache()

        messages.success(
            self.request,
            "Рассылка успешно удалена."
        )

        return response


class ContactsView(TemplateView):
    template_name = "contacts.html"


@login_required
def mailing_statistics_view(request):
    all_attempts = MailingAttempt.objects.all()

    user_attempts = all_attempts.filter(
        client__owner=request.user
    )

    print("Текущий пользователь:", request.user)
    print("Всего попыток в базе:", all_attempts.count())
    print("Попыток пользователя:", user_attempts.count())
    print("Успешных:", user_attempts.filter(status="Успешно").count())
    print("Неуспешных:", user_attempts.filter(status="Не успешно").count())

    statistics = user_attempts.aggregate(
        successful_attempts=Count(
            "id",
            filter=Q(status="Успешно"),
        ),
        unsuccessful_attempts=Count(
            "id",
            filter=Q(status="Не успешно"),
        ),
    )

    statistics["sent_messages"] = statistics["successful_attempts"]

    return render(
        request,
        "service/statistics.html",
        {"statistics": statistics},
    )


@login_required
@user_passes_test(is_manager)
@require_POST
def mailing_disable_view(request, mailing_id):
    mailing = get_object_or_404(Mailing, pk=mailing_id)

    if mailing.status == "Отключена":
        messages.info(request, "Эта рассылка уже отключена.")
    else:
        mailing.status = "Отключена"
        mailing.save(update_fields=["status"])

        clear_mailings_cache()

        messages.success(
            request,
            f"Рассылка №{mailing.pk} успешно отключена."
        )

    return redirect(
        "service:mailing_detail",
        mailing_id=mailing.pk,
    )