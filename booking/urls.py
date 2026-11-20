from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("restaurants/", views.restaurants, name="restaurants"),
    path("register/", views.register, name="register"),
    path("restaurant/<slug:slug>/", views.reserve, name="restaurant"),
    path("my/", views.my_reservations, name="my"),
    path("my/cancel/<int:pk>/", views.cancel, name="cancel"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/reservations/", views.d_reservations, name="d_reservations"),
    path("dashboard/reservations/<int:pk>/<str:status>/", views.d_status, name="d_status"),
    path("dashboard/restaurants/", views.d_restaurants, name="d_restaurants"),
    path("dashboard/tables/", views.d_tables, name="d_tables"),
    path("dashboard/customers/", views.d_customers, name="d_customers"),
]
