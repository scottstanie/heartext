from django.contrib import admin

from .models import User, Snippet, Playlist


admin.site.register(User)
admin.site.register(Snippet)
admin.site.register(Playlist)
