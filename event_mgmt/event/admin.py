from email.headerregistry import Group
from django.contrib import admin
from .models import Event, Ticket, Image, Category
from django.contrib.auth.models import Group

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description', )
    list_filter = ('category', )

# Register your models here.
admin.site.register(Ticket)
admin.site.unregister(Group)

admin.site.register(Image)
admin.site.register(Category)

admin.site.site_header = "Event Admin"