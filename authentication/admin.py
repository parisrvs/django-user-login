from django.contrib import admin
from .models import Person, Address


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    readonly_fields = ("user",)
    list_display = ("user", "first_name", "last_name", "email", "phone", "gender")
    list_filter = ("gender",)
    search_fields = ["user__email", "user__username", "user__first_name", "user__last_name"]

   
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    readonly_fields = ("person",)
    list_filter = ("person", "city", "state", "country")
    list_display = ("person", "address1", "city", "pincode", "mobile")
    empty_value_display = '-empty-'
    search_fields = ["address1", "address2", "landmark"]

