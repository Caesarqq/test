from django.contrib import admin
from .models import Lot, Category, LotCategory, LotImage, DeliveryDetail
from django.utils.html import format_html
from django.contrib import messages

class LotAdmin(admin.ModelAdmin):
    list_display = ('title', 'auction', 'donor', 'status', 'created_at', 'approve_button', 'reject_button')
    list_filter = ('status', 'auction__charity', 'auction')
    search_fields = ('title', 'description', 'donor__email', 'auction__name')
    readonly_fields = ('created_at',)

    def approve_button(self, obj):
        if obj.status == Lot.STATUS_PENDING:
            return format_html('<a class="button" href="{}">Одобрить</a>', f'../approve_lot/{obj.id}/')
        return '-'
    approve_button.short_description = 'Одобрить'
    approve_button.allow_tags = True

    def reject_button(self, obj):
        if obj.status == Lot.STATUS_PENDING:
            return format_html('<a class="button" href="{}">Отклонить</a>', f'../reject_lot/{obj.id}/')
        return '-'
    reject_button.short_description = 'Отклонить'
    reject_button.allow_tags = True

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('approve_lot/<int:lot_id>/', self.admin_site.admin_view(self.approve_lot), name='approve_lot'),
            path('reject_lot/<int:lot_id>/', self.admin_site.admin_view(self.reject_lot), name='reject_lot'),
        ]
        return custom_urls + urls

    def approve_lot(self, request, lot_id):
        lot = Lot.objects.get(pk=lot_id)
        user = request.user
        # Проверка: только организация-владелец аукциона
        if hasattr(user, 'charity') and lot.auction.charity == user.charity:
            if lot.status == Lot.STATUS_PENDING:
                lot.status = Lot.STATUS_APPROVED
                lot.save()
                self.message_user(request, f'Лот "{lot.title}" одобрен.', messages.SUCCESS)
            else:
                self.message_user(request, 'Лот уже не на рассмотрении.', messages.WARNING)
        else:
            self.message_user(request, 'Вы не можете одобрять лоты чужих аукционов.', messages.ERROR)
        from django.shortcuts import redirect
        return redirect(request.META.get('HTTP_REFERER', '/admin/lots/lot/'))

    def reject_lot(self, request, lot_id):
        lot = Lot.objects.get(pk=lot_id)
        user = request.user
        # Проверка: только организация-владелец аукциона
        if hasattr(user, 'charity') and lot.auction.charity == user.charity:
            if lot.status == Lot.STATUS_PENDING:
                lot.status = Lot.STATUS_REJECTED
                lot.save()
                self.message_user(request, f'Лот "{lot.title}" отклонён.', messages.SUCCESS)
            else:
                self.message_user(request, 'Лот уже не на рассмотрении.', messages.WARNING)
        else:
            self.message_user(request, 'Вы не можете отклонять лоты чужих аукционов.', messages.ERROR)
        from django.shortcuts import redirect
        return redirect(request.META.get('HTTP_REFERER', '/admin/lots/lot/'))

admin.site.register(Lot, LotAdmin)
admin.site.register(Category)
admin.site.register(LotCategory)
admin.site.register(LotImage)
admin.site.register(DeliveryDetail)
