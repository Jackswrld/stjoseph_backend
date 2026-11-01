from django.urls import path

from .views import PersonListView

urlpatterns = [
    path("people/", PersonListView.as_view(), name="person-list"),
]