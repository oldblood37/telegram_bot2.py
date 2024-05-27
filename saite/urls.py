from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/', views.main_page, name='main-page'),
    path('aboutus/', views.about_page, name='about-page'),
    path('news/', views.news_page, name='news-page'),
    path('manage_keywords/', views.manage_keywords, name='manage_keywords'),
    path('get_groups/<int:city_id>/', views.get_groups, name='get_groups'),
    path('success/', views.success, name='success'),
]