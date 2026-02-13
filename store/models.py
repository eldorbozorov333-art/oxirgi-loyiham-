from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Mahsulot nomi")
    category = models.CharField(max_length=100, verbose_name="Kategoriya")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Narxi")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Ombordagi miqdor")
    min_limit = models.PositiveIntegerField(default=5, verbose_name="Minimal limit")

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def __str__(self):
        return self.name


class Income(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Mahsulot"
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Kirim narxi (1 dona)"
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Kirim miqdori"
    )
    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        verbose_name="Umumiy summa"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Sana"
    )

    class Meta:
        verbose_name = "Kirim"
        verbose_name_plural = "Kirimlar"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({"quantity": "Miqdor 0 dan katta bo‘lishi kerak"})
        if self.price <= 0:
            raise ValidationError({"price": "Narx 0 dan katta bo‘lishi kerak"})

    def save(self, *args, **kwargs):
        # Har doim validatsiya ishlasin
        self.full_clean()

        # Umumiy summa avto
        self.total_amount = self.price * self.quantity

        # Faqat YANGI kirim bo‘lsa product yangilanadi
        if self.pk is None:
            with transaction.atomic():
                product = Product.objects.select_for_update().get(pk=self.product.pk)
                product.price = self.price
                product.quantity += self.quantity
                product.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - Kirim"


class Expense(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Mahsulot"
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        verbose_name="Sotuv narxi"
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Chiqim miqdori"
    )
    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        verbose_name="Umumiy summa"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Sana"
    )

    class Meta:
        verbose_name = "Chiqim"
        verbose_name_plural = "Chiqimlar"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({"quantity": "Miqdor 0 dan katta bo‘lishi kerak"})

        # clean() ba’zan product hali to‘liq kelmagan bo‘lishi mumkin
        if self.product_id and self.product.quantity < self.quantity:
            raise ValidationError({"quantity": "Omborda yetarli mahsulot yo‘q"})

    def save(self, *args, **kwargs):
        # Har doim validatsiya ishlasin
        self.full_clean()

        # Narx mahsulotdan olinadi
        self.price = self.product.price

        # Umumiy summa avto
        self.total_amount = self.price * self.quantity

        # Faqat YANGI chiqim bo‘lsa ombordagi miqdor kamayadi
        if self.pk is None:
            with transaction.atomic():
                product = Product.objects.select_for_update().get(pk=self.product.pk)

                if product.quantity < self.quantity:
                    raise ValidationError({"quantity": "Omborda yetarli mahsulot yo‘q"})

                product.quantity -= self.quantity
                product.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - Chiqim"


class ActionLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Foydalanuvchi"
    )
    action = models.CharField(max_length=255, verbose_name="Amal")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sana")

    class Meta:
        verbose_name = "Log"
        verbose_name_plural = "Loglar"

    def __str__(self):
        return f"{self.user} - {self.action}"
