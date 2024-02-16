from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount_of_cases', 'is_traded']
    list_editable = ['is_traded']
    readonly_fields = ('amount_of_cases',)

admin.site.register(User, UserAdmin)