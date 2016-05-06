from django.conf import settings
from django.contrib import admin
from ballot_box.models import ResultSource, Election
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")

class ResultSourceAdmin(admin.ModelAdmin):
    list_display = ("source_name", "source_active", "source_created")
    list_per_page = 15
    list_filter = ["source_name"]
    ordering = ["source_name"]
    save_on_top = True


class ElectionAdmin(admin.ModelAdmin):
    list_display = ("type", "election_date", "test_results", "live_results")
    list_per_page = 15
    # list_filter = ["source_name"]
    # ordering = ["source_name"]
    save_on_top = True


admin.site.register(ResultSource, ResultSourceAdmin)
admin.site.register(Election, ElectionAdmin)
