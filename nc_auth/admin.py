from django.contrib import admin

from nc_auth.models import User, Token

admin.site.register(User)
admin.site.register(Token)
