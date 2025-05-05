from django.urls import path
from . import views

urlpatterns = [
    path('process_ticket/', views.process_ticket, name='process_ticket'),
]