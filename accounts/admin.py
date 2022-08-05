from django.contrib import admin
from .models import User
from .models import UserProfile


class UserAdmin(admin.ModelAdmin):

    list_display=('username','email','user_type', 'is_email_verified')
    search_fields =('username','email','user_type', 'is_email_verified')
    list_per_page=25


    

admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)