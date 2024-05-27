
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from telegram_auth import views as telegram_auth_views
from saite import views as saite_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('telegram_auth/', include('telegram_auth.urls')),
    path('telegram-webhook', telegram_auth_views.telegram_webhook, name='telegram_webhook'),
    path('', saite_views.main_page, name='main-page'),
    path('aboutus/', saite_views.about_page, name='about-page'),
    path('news/', saite_views.news_page, name='news-page'),
    path('setings/', saite_views.manage_keywords, name='settings-page'),
    path('login/', telegram_auth_views.login_by_token, name='login-by-token'),

]
