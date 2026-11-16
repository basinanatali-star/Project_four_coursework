from django.contrib import admin
from service.models import Client, Message, Mailing, MailingAttempt

admin.site.register(Client)
admin.site.register(Message)
admin.site.register(MailingAttempt)

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "start_time", "end_time", "status", "current_status")

    @admin.display(description="Актуальный статус")
    def current_status(self, obj):
        return obj.current_status
