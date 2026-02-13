from django.contrib import admin
from .models import Product, Income, Expense
from django.db.models import Sum
from django.contrib.admin import AdminSite
from .models import ActionLog



# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'quantity', 'holat')
    search_fields = ('name',)
    list_filter = ('category',)

    def holat(self, obj):
        if obj.quantity == 0:
            return "❌ Tugagan"
        elif obj.quantity < 5:
            return "⚠️ Kam qolgan"
        else:
            return "✅ Yetarli"

    holat.short_description = "Holati"

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name="Sotuvchilar").exists():
            return False
        return super().has_change_permission(request, obj)




@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'quantity', 'total_amount', 'created_at')
    readonly_fields = ('total_amount',)
    list_filter = ('created_at',)

    def save_model(self, request, obj, form, change):
            yangi = not obj.pk
            super().save_model(request, obj, form, change)

            if yangi:
                ActionLog.objects.create(
                    user=request.user,
                    action=f"{obj.product.name} mahsulotiga {obj.quantity} dona chiqim qilindi"
                )

    verbose_name = "Kirim"
    verbose_name_plural = "Kirimlar"
    def jami_kirim(self, request):
        result = Income.objects.aggregate(total=Sum('total_amount'))
        return result['total'] or 0

    jami_kirim.short_description = "Jami kirim summasi"

    def has_view_permission(self, request, obj=None):
        if request.user.groups.filter(name="Sotuvchilar").exists():
            return False
        return super().has_view_permission(request, obj)

       


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'quantity', 'total_amount', 'created_at')
    readonly_fields = ('price', 'total_amount')
    list_filter = ('created_at',)

    def save_model(self, request, obj, form, change):
        yangi = not obj.pk
        super().save_model(request, obj, form, change)

        if yangi:
            ActionLog.objects.create(
                user=request.user,
                action=f"{obj.product.name} mahsulotidan {obj.quantity} dona chiqim qilindi"
            )


    verbose_name = "Chiqim"
    verbose_name_plural = "Chiqimlar"

    def jami_chiqim(self, request):
        result = Expense.objects.aggregate(total=Sum('total_amount'))
        return result['total'] or 0

    jami_chiqim.short_description = "Jami chiqim summasi"

class MyAdminSite(AdminSite):
    site_header = "🛒 Do'kon boshqaruv paneli"
    site_title = "Do'kon Admin"
    index_title = "Statistika va boshqaruv"

class DashboardAdmin(AdminSite):
    site_header = "📊 Do'kon statistikasi"


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('action',)
    readonly_fields = ('user', 'action', 'created_at')

    def has_add_permission(self, request):
        return False


admin.site.site_header = "🛒 Do'kon boshqaruv paneli"
admin.site.site_title = "Do'kon Admin"
admin.site.index_title = "Statistika va boshqaruv"
