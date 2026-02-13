from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.utils.timezone import now
from django.core.exceptions import ValidationError

from .models import Product, Income, Expense, ActionLog
from .forms import ExpenseForm, IncomeForm


@login_required
def home(request):
    jami_kirim = Income.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    jami_chiqim = Expense.objects.aggregate(total=Sum('total_amount'))['total'] or 0

    mahsulot_soni = Product.objects.count()
    tugaganlar = Product.objects.filter(quantity=0)
    tugagan_soni = tugaganlar.count()
    kam_qolganlar = Product.objects.filter(quantity__lte=F('min_limit')).order_by('quantity')

    products = Product.objects.all().order_by('id')

    context = {
        'jami_kirim': jami_kirim,
        'jami_chiqim': jami_chiqim,
        'mahsulot_soni': mahsulot_soni,
        'tugaganlar': tugaganlar,
        'tugagan_soni': tugagan_soni,
        'kam_qolganlar': kam_qolganlar,
        'products': products,
    }
    return render(request, 'home.html', context)


@login_required
def kirim_qilish(request):
    form = IncomeForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        try:
            income = form.save()  # Income.save() avtomatik: total_amount, product.price va product.quantity yangilanadi

            ActionLog.objects.create(
                user=request.user,
                action=f"Kirim: {income.product.name} - {income.quantity} dona (narx: {income.price})"
            )
            return redirect('kirim')

        except ValidationError as e:
            form.add_error(None, e)

    return render(request, 'kirim.html', {'form': form})


@login_required
def chiqim_qilish(request):
    form = ExpenseForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        try:
            expense = form.save()  # Expense.save() avtomatik: total_amount, ombordagi quantity kamayadi

            ActionLog.objects.create(
                user=request.user,
                action=f"Chiqim: {expense.product.name} - {expense.quantity} dona"
            )
            return redirect('chiqim')

        except ValidationError as e:
            form.add_error(None, e)

    return render(request, 'chiqim.html', {'form': form})


@login_required
def hisobot(request):
    today = now().date()

    # Bugungi chiqim (savdo)
    bugungi_chiqimlar = Expense.objects.filter(created_at__date=today).select_related('product').order_by('-created_at')
    bugungi_chiqim = bugungi_chiqimlar.aggregate(total=Sum('total_amount'))['total'] or 0

    # Bugungi kirim
    bugungi_kirimlar = Income.objects.filter(created_at__date=today).select_related('product').order_by('-created_at')
    bugungi_kirim = bugungi_kirimlar.aggregate(total=Sum('total_amount'))['total'] or 0

    # Umumiy (hamma vaqt)
    jami_kirim = Income.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    jami_chiqim = Expense.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    foyda = Decimal(jami_chiqim) - Decimal(jami_kirim)

    context = {
        'today': today,

        'bugungi_kirim': bugungi_kirim,
        'bugungi_chiqim': bugungi_chiqim,

        'jami_kirim': jami_kirim,
        'jami_chiqim': jami_chiqim,
        'foyda': foyda,

        'bugungi_kirimlar': bugungi_kirimlar[:50],
        'bugungi_chiqimlar': bugungi_chiqimlar[:50],
    }
    return render(request, 'hisobot.html', context) 