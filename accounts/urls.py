from django.urls import path, include
from . import views

urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('login', views.login_user, name='login_user'),
    path('logout', views.logout_user, name='logout_user'),
    path('profile/<int:user_id>', views.profile, name="profile"),
    path('activate-user/<uidb64>/<token>',
         views.activate_user, name='activate'),
]
