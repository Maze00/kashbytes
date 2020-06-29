from django.shortcuts import render, redirect
from django.views import View
from frontend.models import *
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import socket
from backend.forms import ChangeUserDataForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime, now
from datetime import timedelta

User = get_user_model()


# ---------------------------------------------------------------
# This is admin index page
# ---------------------------------------------------------------
class AdminIndex(View):
    template_name = "backend/home.html"

    def get(self, request):
        context = {}
        context["users"] = User.objects.all().order_by("-id")
        context["active_users"] = len(User.objects.filter(is_active=True, is_superuser=False).all())
        context["suspended_users"] = len(User.objects.filter(is_active=False, is_superuser=False).all())
        try:
            context["coins"] = CashAndCoinsTable.objects.all()
            context["transfer_coins"] = TransferCoins.objects.all()
            context["received_coins"] = ReceiveCoins.objects.all()
            context["cash_out_coins"] = CashOutRequestTable.objects.all()
            context["bonus_coins"] = AccountActivationCoins.objects.all()

            context["total_coin"] = 0
            context["total_transferred_coins"] = 0
            context["total_received_coins"] = 0
            context["total_cash_out_coins"] = 0
            context["total_bonus_coins"] = 0

            for coin in context["coins"]:
                context["total_coin"] += coin.user_coins

            for coin in context["transfer_coins"]:
                context["total_transferred_coins"] += coin.coins

            for coin in context["received_coins"]:
                context["total_received_coins"] += coin.coins

            for coin in context["cash_out_coins"]:
                context["total_cash_out_coins"] += coin.coins

            for coin in context["bonus_coins"]:
                context["total_bonus_coins"] += coin.coins

            context["total_joined_coins"] = (context["total_coin"] + context["total_received_coins"] + context[
                "total_bonus_coins"]) - (context["total_transferred_coins"] + context["total_cash_out_coins"])

            context["total_cash"] = int(context["total_joined_coins"]) * 100
        except CashAndCoinsTable.DoesNotExist or TransferCoins.DoesNotExist or ReceiveCoins.DoesNotExist:
            pass
        return render(request, self.template_name, context)


# ---------------------------------------------------------------
# This page will display all the users data
# ---------------------------------------------------------------
class AdminUsers(View):
    template_name = "backend/users.html"

    def get(self, request):
        context = {}
        page = request.GET.get('page', 1)
        users = User.objects.all().order_by("-id")
        paginator = Paginator(users, 10)
        try:
            context["users"] = paginator.page(page)
        except PageNotAnInteger:
            context["users"] = paginator.page(1)
        except EmptyPage:
            context["users"] = paginator.page(paginator.num_pages)

        return render(request, self.template_name, context)


# ---------------------------------------------------------------
# This page will display all the payment details
# ---------------------------------------------------------------
class PaymentDetails(View):
    template_name = "backend/payments.html"

    def get(self, request):
        context = {}
        all = ProfileLevel.objects.all().filter(pay_by_user__gt=0).order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(all, 10)
        try:
            context["all"] = paginator.page(page)
        except PageNotAnInteger:
            context["all"] = paginator.page(1)
        except EmptyPage:
            context["all"] = paginator.page(paginator.num_pages)
        return render(request, self.template_name, context)


# ---------------------------------------------------------------
# This function will help to approve payments and others
# activities
# ---------------------------------------------------------------
def approve_payment(request, id):
    profile_level = ProfileLevel.objects.get(user_id=id)
    profile_level.review = True
    profile_level.has_paid = False

    call_by = profile_level.user.call_by

    if call_by is not None:

        if profile_level.pay_by_user == 1800:
            profile_level.coins = 18
            profile_level.user_level = 1
            profile_level.review = True
            profile_level.has_paid = False
            profile_level.active_with_pay = True
            profile_level.save()

            pay = User.objects.get(id=id)
            pay.payment_done = True
            pay.save()

        random_number = random.randint(10000000, 100000000000)

        if ReferralUrl.objects.filter(user_id=id).exists():
            url = ReferralUrl.objects.get(user_id=id)
            url.url_address = random_number
            url.url_validity = False
            url.self_register = False
            url.save()
        else:
            ReferralUrl.objects.create(url_address=random_number, url_validity=False, user_id=id, self_register=False)

        CashAndCoinsTable.objects.create(user_cash=profile_level.pay_by_user, user_coins=profile_level.coins,
                                         user_id=id)
        return redirect("payment_details")

    else:

        if profile_level.pay_by_user == 1800:
            profile_level.coins = 18
            profile_level.user_level = 1

        profile_level.active_with_pay = True
        profile_level.review = True
        profile_level.has_paid = False
        profile_level.save()

        pay = User.objects.get(id=id)
        pay.payment_done = True
        pay.save()
    random_number = random.randint(10000000, 100000000000)

    if ReferralUrl.objects.filter(user_id=id).exists():
        url = ReferralUrl.objects.get(user_id=id)
        url.url_address = random_number
        url.url_validity = False
        url.self_register = False
        url.save()
    else:
        ReferralUrl.objects.create(url_address=random_number, url_validity=False, user_id=id, self_register=False)

    CashAndCoinsTable.objects.create(user_cash=profile_level.pay_by_user, user_coins=profile_level.coins,
                                     user_id=id)
    return redirect("payment_details")


# ---------------------------------------------------------------
# This function will assist to disapprove payment if need
# ---------------------------------------------------------------
def disapprove_payment(request, id):
    profile_level = ProfileLevel.objects.get(user_id=id)
    profile_level.pay_by_user = 0
    profile_level.review = 0
    profile_level.coins = 0
    profile_level.transaction_id = None
    profile_level.has_paid = 0
    profile_level.save()

    try:
        subject = "Bonus Notification"
        message = f"Hello {profile_level.user.username},\n" \
                  f"Your bkash transaction was neglected due to incorrect ID number."
        from_email = settings.EMAIL_HOST_USER
        receiver = [profile_level.user.email, ]
        send_mail(subject, message, from_email, receiver)
    except socket.error:
        messages.error(request, "Server response time out, try again!!",
                       extra_tags="request_url_sent_error")
    return redirect("payment_details")


# ---------------------------------------------------------------
# This page will hols details of all payments
# ---------------------------------------------------------------
class AllPaymentsByUsers(View):

    template_name = "backend/all_payments.html"

    def get(self, request):
        context = {}
        page = request.GET.get('page', 1)
        try:
            payments = CashAndCoinsTable.objects.all().order_by('-user')
        except CashAndCoinsTable.DoesNotExist:
            payments = None
        paginator = Paginator(payments, 10)
        try:
            context["payments"] = paginator.page(page)
        except PageNotAnInteger:
            context["payments"] = paginator.page(1)
        except EmptyPage:
            context["payments"] = paginator.page(paginator.num_pages)
        return render(request, self.template_name, context)


# ---------------------------------------------------------------
# Cash out request checking query from admin
# ---------------------------------------------------------------
class CashOutRequest(View):
    template_name = "backend/cash_out_request.html"

    def get(self, request):
        context = {}
        try:
            cash_out_request = CashOutRequestTable.objects.all().order_by("-id")
            page = request.GET.get('page', 1)

            paginator = Paginator(cash_out_request, 10)
            try:
                context["cash_out_request"] = paginator.page(page)
            except PageNotAnInteger:
                context["cash_out_request"] = paginator.page(1)
            except EmptyPage:
                context["cash_out_request"] = paginator.page(paginator.num_pages)
        except CashOutRequestTable.DoesNotExist:
            pass
        return render(request, self.template_name, context)


# ---------------------------------------------------------------
# Cash out request approval function
# ---------------------------------------------------------------
def cash_out_request_approve(request, id):
    template_name = "backend/cash_out_request.html"
    try:
        cash_out = CashOutRequestTable.objects.get(id=id)
        cash_out.is_done = True
        cash_out.is_approve = True
        cash_out.save()

        try:
            subject = "Requested Cash Out From KashBytes"
            message = f"Hello {cash_out.ask_by.username},\n" \
                      f"We have sent you {cash_out.cash} BDT cash in bkash, please check balance."
            from_email = settings.EMAIL_HOST_USER
            receiver = [cash_out.ask_by.email, ]
            send_mail(subject, message, from_email, receiver)
            return redirect('cash_out_approve')
        except socket.error:
            messages.error(request, "Server response time out, try again!!",
                           extra_tags="request_url_sent_error")
        return redirect("cash_out_request")
    except:
        pass
    return render(request, template_name)


# ---------------------------------------------------------------
# Cash out request refuse function
# ---------------------------------------------------------------
def cash_out_request_refuse(request, id):
    template_name = "backend/cash_out_request.html"
    try:
        cash_out = CashOutRequestTable.objects.get(id=id)
        cash_out.is_done = True
        cash_out.is_approve = False
        cash_out.cash = 0
        cash_out.coins = 0
        cash_out.save()

        try:
            subject = "Requested Cash Out From KashBytes"
            message = f"Hello {cash_out.ask_by.username},\n" \
                      f"We have refused sent you {cash_out.cash} " \
                      f"BDT cash in bkash due to some reason, please check balance."
            from_email = settings.EMAIL_HOST_USER
            receiver = [cash_out.ask_by.email, ]
            send_mail(subject, message, from_email, receiver)
            return redirect('cash_out_approve')
        except socket.error:
            messages.error(request, "Server response time out, try again!!",
                           extra_tags="request_url_sent_error")

        return redirect("cash_out_request")
    except:
        pass
    return render(request, template_name)


# ---------------------------------------------------------------
# User data update view from admin
# ---------------------------------------------------------------
class EditDetails(View):
    template_name = "backend/details.html"

    def get(self, request, id):
        context = {}
        context["details_data"] = User.objects.get(id=id)
        if context["details_data"].is_active is True:
            action = True
        else:
            action = False
        context["change_user_data_form"] = ChangeUserDataForm(
            initial={
                action: action
            }
        )
        try:
            context["transfer_coins"] = TransferCoins.objects.filter(given_by=id).all()
            context["received_coins"] = ReceiveCoins.objects.filter(receive_by=id).all()
            context["cash_out_coins"] = CashOutRequestTable.objects.filter(ask_by=id).all()
            context["bonus_coins"] = AccountActivationCoins.objects.filter(send_to=id).all()
            context["bonus_coins_fh"] = HostBuyCash.objects.filter(send_to=id, approve=True).all()

            context["total_transferred_coins"] = 0
            context["total_received_coins"] = 0
            context["total_cash_out_coins"] = 0
            context["total_bonus_coins"] = 0
            context["total_from_hots_coins"] = 0

            for coin in context["transfer_coins"]:
                context["total_transferred_coins"] += coin.coins

            for coin in context["received_coins"]:
                context["total_received_coins"] += coin.coins

            for coin in context["cash_out_coins"]:
                context["total_cash_out_coins"] += coin.coins

            for coin in context["bonus_coins"]:
                context["total_bonus_coins"] += coin.coins

            for coin in context["bonus_coins_fh"]:
                context["total_bonus_coins"] += coin.coins

            context["total_joined_coins"] = (context["total_received_coins"] + context["total_bonus_coins"] +
                                                context["total_from_hots_coins"]) - (
                                                           context["total_transferred_coins"] + context[
                                                       "total_cash_out_coins"])
            context["total_joined_cash"] = context["total_joined_coins"] * 100
        except CashAndCoinsTable.DoesNotExist or TransferCoins.DoesNotExist or ReceiveCoins.DoesNotExist or HostBuyCash.DoesNotExist:
            pass
        return render(request, self.template_name, context)

    def post(self, request, id):
        context = {}
        context["details_data"] = User.objects.get(id=id)
        if context["details_data"].user.is_active is True:
            action = True
        else:
            action = False
        context["change_user_data_form"] = ChangeUserDataForm(request.POST,
                                                              initial={
                                                                  action: action
                                                              }
                                                              )
        if context["change_user_data_form"].is_valid():
            action_data = context["change_user_data_form"].cleaned_data.get("action", None)
            data = User.objects.get(id=context['details_data'].user_id)
            data.is_active = action_data
            data.save()
            return redirect("admin_users")
        return render(request, self.template_name, context)


class Reports(View):

    template_name = 'backend/reports.html'

    def get(self, request):
        context = {}
        try:
            reports = CashAndCoinsTable.objects.all()
            for report in reports:

                dby = report.created_at.date_joined - timedelta(days=2)
                y = report.created_at.date_joined - timedelta(days=1)

                last_day_before = CashAndCoinsTable.objects.filter(created_at=dby)
                last_day = CashAndCoinsTable.objects.filter(created_at=y)

        except CashAndCoinsTable.DoesNotExist:
            pass
        return render(request, self.template_name, context)


class BuyCashApplies(View):

    template_name = "backend/buy_cash.html"

    def get(self, request):
        context = {}
        context["applies_data"] = HostBuyCash.objects.all().order_by('-id')
        return render(request, self.template_name, context)


def approve_buying_from_host(request, id):
    data = HostBuyCash.objects.get(id=id)
    coins = data.cash/100
    data.coins = coins
    data.is_seen = True
    data.approve = True
    data.save()

    return redirect('buy_cash_applies')


def disapprove_buying_from_host(request, id):
    data = HostBuyCash.objects.get(id=id)
    data.delete()

    return redirect('buy_cash_applies')
