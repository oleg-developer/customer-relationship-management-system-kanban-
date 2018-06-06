from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter

from nc_core.models.dataitems import *
from .models import *


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(ClientExtraTypeFace)
class ClientExtraTypeFaceAdmin(admin.ModelAdmin):
    pass


# ====== DataItems ======

class DataItemsBaseChildAdmin(PolymorphicChildModelAdmin):
    base_model = DataItem


@admin.register(Address)
class AddressAdmin(DataItemsBaseChildAdmin):
    base_model = Address


@admin.register(Email)
class EmailAdmin(DataItemsBaseChildAdmin):
    base_model = Email


@admin.register(PhoneNumber)
class PhoneNumberAdmin(DataItemsBaseChildAdmin):
    base_model = PhoneNumber


@admin.register(Skype)
class SkypeAdmin(DataItemsBaseChildAdmin):
    base_model = Skype


@admin.register(WebSite)
class WebSiteAdmin(DataItemsBaseChildAdmin):
    base_model = WebSite


@admin.register(DataItem)
class ModelAParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = DataItem
    child_models = (Address, Email, PhoneNumber, Skype, WebSite)
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.
