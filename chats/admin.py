from django.contrib import admin
from .models import Messages,CustomGroups, Conversation

admin.site.register(Messages)
admin.site.register(CustomGroups)
admin.site.register(Conversation)
