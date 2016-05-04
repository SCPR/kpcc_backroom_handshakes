from django.conf import settings
from django.contrib import admin
from ballot_box.models import ResultSource
import logging


logger = logging.getLogger("kpcc_backroom_handshakes")


class ResultSourceAdmin(admin.ModelAdmin):
    list_display = ("source_name", "source_active", "source_created")
    list_per_page = 15
    list_filter = ["source_name"]
    ordering = ["source_name"]
    save_on_top = True
    # prepopulated_fields = {
    #     'initiative_slug': ('initiative_identifier',)
    # }

admin.site.register(ResultSource, ResultSourceAdmin)
