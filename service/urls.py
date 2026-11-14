from django.urls import path
from service.apps import ServiceConfig
from service.views import ClientsListView, ClientCreateView, ClientDetailView, ClientUpdateView, ClientDeleteView, \
    HomeView

app_name = ServiceConfig.name

class UnpublishClientView:
    pass

urlpatterns = [
    path("",HomeView.as_view() , name="index"),
    path("client/", ClientsListView.as_view(), name="clients_list"),
    path("client/create/", ClientCreateView.as_view(), name="client_create"),
    path(
        "client/<int:client_id>/", ClientDetailView.as_view(), name="client_detail"
    ),
    path(
        "client/<int:client_id>/edit/",
        ClientUpdateView.as_view(),
        name="client_update",
    ),
    path(
        "client/<int:client_id>/delete/",
        ClientDeleteView.as_view(),
        name="client_delete",
    ),

]
