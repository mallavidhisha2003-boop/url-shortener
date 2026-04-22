from django.contrib import admin
from django.urls import path
from shortener import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('stats/', views.stats_view),   # ✅ FIRST
    path('', views.create_short_url),
    path('<str:code>/', views.redirect_url),  # ✅ LAST
]