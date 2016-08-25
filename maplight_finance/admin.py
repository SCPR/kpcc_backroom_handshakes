# Register your models here.
# from maplight_finance.models import Initiative, InitiativeContributor
from django.conf import settings
from django.contrib import admin
from django.utils.timezone import utc, localtime
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")


# class InitiativeContributorAdmin(admin.ModelAdmin):
#     list_display = ("name", "zip_code", "amount")
#     list_per_page = 15
#     search_fields = ["name"]
#     #list_filter = ["initiative_identifier"]
#     ordering = ["-amount"]


# class InitiativeContributorInline(admin.StackedInline):
#     model = InitiativeContributor
#     extra = 1


# class InitiativeAdmin(admin.ModelAdmin):
#     list_display = ("initiative_identifier", "description")
#     list_per_page = 15
#     list_filter = ["initiative_identifier"]
#     ordering = ["initiative_identifier"]
#     inlines = (InitiativeContributorInline, )
#     save_on_top = True
#     prepopulated_fields = {
#         'initiative_slug': ('initiative_identifier',)
#     }

# admin.site.register(Initiative, InitiativeAdmin)
# admin.site.register(InitiativeContributor, InitiativeContributorAdmin)
