from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('kirim/', views.kirim_qilish, name='kirim'),
    path('chiqim/', views.chiqim_qilish, name='chiqim'),
    path('hisobot/', views.hisobot, name='hisobot'),
]  