from django.contrib import admin
from .models import KhojTheSearch

# Register your models here.
class KhojTheSearchAdmin(admin.ModelAdmin):
    list_display = ('user', 'int_list', 'created_at',)
    
admin.site.register(KhojTheSearch, KhojTheSearchAdmin)