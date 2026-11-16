from django.urls import path
from service.apps import ServiceConfig
from service.views import ClientsListView, ClientCreateView, ClientDetailView, ClientUpdateView, ClientDeleteView, \
    HomeView, mailing_send_view, MailingDetailView, MailingListView, MessageListView, MessageCreateView, \
    MessageDetailView, MessageUpdateView, MessageDeleteView, MailingCreateView, MailingDeleteView, ContactsView, \
    mailing_statistics_view, users_list_view, user_block_view, mailing_disable_view, MailingUpdateView

app_name = ServiceConfig.name

urlpatterns = [
    path("",HomeView.as_view() , name="index"),
    path("clients/", ClientsListView.as_view(), name="clients_list"),
    path("clients/create/", ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:client_id>/", ClientDetailView.as_view(), name="client_detail"),
    path("clients/<int:client_id>/update/", ClientUpdateView.as_view(), name="client_update"),
    path("clients/<int:client_id>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    path("messages/", MessageListView.as_view(), name="messages_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:message_id>/", MessageDetailView.as_view(), name="message_detail"),
    path("messages/<int:message_id>/update/", MessageUpdateView.as_view(), name="message_update"),
    path("messages/<int:message_id>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    path("mailings/", MailingListView.as_view(), name="mailings_list"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailings/<int:mailing_id>/send/", mailing_send_view, name="mailing_send"),
    path("mailings/<int:mailing_id>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailings/<int:mailing_id>/update/", MailingUpdateView.as_view(), name="mailing_update"),
    path("mailings/<int:mailing_id>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("statistics/", mailing_statistics_view, name="statistics"),
    path("users/", users_list_view, name="users_list"),
    path("users/<int:user_id>/block/", user_block_view, name="user_block"),
    path("mailings/<int:mailing_id>/disable/", mailing_disable_view, name="mailing_disable"),
]
