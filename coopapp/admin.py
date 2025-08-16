from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

from users.admin import UserAdmin  # noqa: E402

admin.site.register(User, UserAdmin)
