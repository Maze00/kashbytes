from django.shortcuts import render, redirect
from django.views import View
from django.core.mail import send_mail
from frontend.forms import *
from django.conf import settings
from django.contrib import messages
import random
from frontend.models import *
from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password
import socket
from django.utils.timezone import localtime, now
from datetime import timedelta, date

User = get_user_model()

# ---------------------------------------------
# Global Variable Main domain address
# ---------------------------------------------
global_domain_name = "http://127.0.0.1:8000"


# ---------------------------------------------------------------
# Home page from frontend
# ---------------------------------------------------------------
class HomePage(View):

    template_name = "frontend/index.html"

    def get(self, request):
        context = {}
        context["email_form"] = RequestReferralForm()
        return render(request, self.template_name, context)

    def post(self, request):
        context = {}
        context["email_form"] = RequestReferralForm(request.POST)

        if context["email_form"].is_valid():
            email = context["email_form"].cleaned_data.get("email_address", None)
            random_number = random.randint(10000000, 100000000000)
            try:
                subject = "Requested Url From KashBytes"
                message = f"Your requested registration url is : " \
                          f"{global_domain_name}/user/signup/{random_number}/"
                from_email = settings.EMAIL_HOST_USER
                receiver = [email, ]
                sent = send_mail(subject, message, from_email, receiver)
                if sent:
                    ReferralUrl.objects.create(url_address=random_number)
                messages.success(request, "Url has been sent to your mail!", extra_tags="request_url_sent_success")
            except socket.error:
                messages.error(request, "Server response time out, try again!!", extra_tags="request_url_sent_error")
        return render(request, self.template_name, context)


# ---------------------------------------------------------------
# About page from frontend
# ---------------------------------------------------------------
class AboutPage(View):

    template_name = "frontend/about-us.html"

    def get(self, request):
        return render(request, self.template_name)


# ---------------------------------------------------------------
# Learn more page from frontend
# ---------------------------------------------------------------
class LearMorePage(View):

    template_name = "frontend/learn-more.html"

    def get(self, request):
        return render(request, self.template_name)


# ---------------------------------------------------------------
# User registration page from frontend
# ---------------------------------------------------------------
class UserRegistration(View):

    template_name = "frontend/signup.html"

    def get(self, request, url):
        context = {}
        context["signup_form"] = RegistrationForm()
        return render(request, self.template_name, context)

    def post(self, request, url):
        context = {}
        context["signup_form"] = RegistrationForm(request.POST)

        if context["signup_form"].is_valid():
            try:
                valid_url = ReferralUrl.objects.get(url_address=url)
            except ReferralUrl.DoesNotExist:
                messages.error(request, "Invalid url passed to get registered!", extra_tags="url_validation_error")
                return redirect(f"/user/signup/{url}/")

            if bool(valid_url.url_validity) is True:
                messages.error(request, "Url already used, get another!", extra_tags="url_validation_error")
                return redirect(f"/user/signup/{url}/")
            else:
                username = context["signup_form"].cleaned_data.get("username", None)
                email = context["signup_form"].cleaned_data.get("email", None)
                password = context["signup_form"].cleaned_data.get("password", None)
                password = make_password(password)
                mobile_number = context["signup_form"].cleaned_data.get("mobile_number", None)
                date_of_birth = context["signup_form"].cleaned_data.get("date_of_birth", None)
                gender = context["signup_form"].cleaned_data.get("gender", None)

                if valid_url.user is None:
                    valid_url.url_validity = True
                    valid_url.self_register = True
                    valid_url.user = None
                    User.objects.create(
                        username=username,
                        email=email,
                        password=password,
                        mobile_number=mobile_number,
                        date_of_birth=date_of_birth,
                        sex=gender,
                        call_by=None
                    )
                else:
                    valid_url.url_validity = False
                    valid_url.self_register = False
                    valid_url.user = valid_url.user
                    User.objects.create(
                        username=username,
                        email=email,
                        password=password,
                        mobile_number=mobile_number,
                        date_of_birth=date_of_birth,
                        sex=gender,
                        call_by=valid_url.user.id
                    )
                user = User.objects.get(email=email)
                ProfileLevel.objects.create(user_id=user.id)
                valid_url.save()

                messages.success(request, "Account successfully registered!", extra_tags="registration_success")
                return redirect("user_login")
        return render(request, self.template_name, context)


# ---------------------------------------------------------------
# User login page from frontend
# ---------------------------------------------------------------
class UserLogin(View):

    template_name = "frontend/login.html"

    def get(self, request):
        context = {}
        context['login_form'] = UserLoginForm(request.POST)
        return render(request, self.template_name, context)

    def post(self, request):
        context = {}
        context['login_form'] = UserLoginForm(request.POST)

        if context['login_form'].is_valid():
            username = context['login_form'].cleaned_data.get('user', None)
            password = context['login_form'].cleaned_data.get('password', None)

            user = authenticate(user=username, password=password)
            if user:
                if user.is_active is bool(True):
                    login(request, user)
                    if user.is_superuser is bool(False):
                        return redirect('user_profile')
                    else:
                        return redirect("admin_index")
                else:
                    context['error_msg'] = 'Your account is suspended!'
                    return render(request, self.template_name, context)
            else:
                context['error_msg'] = 'Invalid credentials provided!'
                return render(request, self.template_name, context)

        return render(request, self.template_name, context)


# ---------------------------------------------------------------
# Logout option for frontend
# ---------------------------------------------------------------
class UserLogout(View):

    def get(self, request):
        logout(request)
        return redirect('user_login')


# ---------------------------------------------------------------
# Forget password section for website
# ---------------------------------------------------------------
class ForgetPassword(View):

    template_name = "frontend/forget.html"

    def get(self, request):
        context = {}
        context["email_form"] = ForgotPasswordForm()
        return render(request, self.template_name, context)

    def post(self, request):
        context = {}
        context["email_form"] = ForgotPasswordForm(request.POST)

        if context["email_form"].is_valid():
            email = context["email_form"].cleaned_data.get("email", None)
            user = User.objects.get(email=email)
            random_number = random.randint(10000000, 100000000000)
            try:
                subject = "Password Recovery Url"
                message = f"Your requested registration url is : " \
                          f"{global_domain_name}/user/recover-password/{random_number}/"
                from_email = settings.EMAIL_HOST_USER
                receiver = [email, ]
                sent = send_mail(subject, message, from_email, receiver)
                if sent:
                    if not PasswordRecoveryUrl.objects.filter(user_id=user.id).exists():
                        PasswordRecoveryUrl.objects.create(
                            url=random_number,
                            created_at=localtime(now()).date(),
                            user=user
                        )
                    else:
                        data = PasswordRecoveryUrl.objects.get(user_id=user.id)
                        data.url = random_number
                        data.validity = False
                        data.created_at = localtime(now()).date(),
                        data.save()
                messages.success(request, "Url has been sent to your mail!", extra_tags="request_url_sent_success")
            except socket.error:
                messages.error(request, "Server response time out, try again!!", extra_tags="request_url_sent_error")
        return redirect("f_home_page")


# ---------------------------------------------------------------
# Password recovery option for the website
# ---------------------------------------------------------------
class PasswordRecovery(View):

    template_name = "frontend/password-recovery.html"

    def get(self, request, url):
        context = {}
        try:
            recovery_url = PasswordRecoveryUrl.objects.get(url=url)
            recovery_url.updated_at = localtime(now()).date()
            recovery_url.save()
        except:
            pass

        context["change_password_form"] = ChangePasswordForm()
        return render(request, self.template_name, context)

    def post(self, request, url):
        context = {}
        context["change_password_form"] = ChangePasswordForm(request.POST)

        if context["change_password_form"].is_valid():
            try:
                valid_url = PasswordRecoveryUrl.objects.get(url=url)
            except PasswordRecoveryUrl.DoesNotExist:
                messages.error(request, "Invalid url passed to change password!", extra_tags="url_validation_error")
                return redirect(f"/user/recover-password/{url}/")

            if bool(valid_url.validity) is True:
                messages.error(request, "Url already used, get another!", extra_tags="url_validation_error")
                return redirect(f"/user/recover-password/{url}/")
            else:
                recovery_url = PasswordRecoveryUrl.objects.get(url=url)
                password = context["change_password_form"].cleaned_data.get("password", None)
                password = make_password(password)
                if recovery_url.created_at == recovery_url.updated_at:
                    recovery_url.validity = True
                    user = User.objects.get(id=recovery_url.user_id)
                    user.password = password
                    user.save()
                    recovery_url.save()
                    messages.success(request, "Password successfully changed!", extra_tags="password_change_success")
                    return redirect("user_login")
                else:
                    messages.error(request, "Url validity is expired!", extra_tags="password_change_error")
        return render(request, self.template_name, context)


# ---------------------------------------------------------------
# User profile page from website
# ---------------------------------------------------------------
class UserProfile(View):

    template_name = "frontend/user_views/index.html"

    def get(self, request):
        context = {}
        try:
            context["refer_url"] = ReferralUrl.objects.get(user=request.user)
        except ReferralUrl.DoesNotExist:
            pass
        try:
            context["user_level"] = ProfileLevel.objects.get(user=request.user)
        except ProfileLevel.DoesNotExist:
            pass
        try:
            context["transfer_coins"] = TransferCoins.objects.filter(given_by=request.user.id).all()
            context["received_coins"] = ReceiveCoins.objects.filter(receive_by=request.user.id).all()
            context["cash_out_coins"] = CashOutRequestTable.objects.filter(ask_by=request.user.id).all()
            context["bonus_coins"] = AccountActivationCoins.objects.filter(send_to=request.user.id).all()
            context["bonus_coins_fh"] = HostBuyCash.objects.filter(send_to=request.user.id, approve=True).all()
            context["bonus_coins_3days"] = ReceiveCoins3daysOffer.objects.filter(receive_by=request.user.id).all()

            context["total_transferred_coins"] = 0
            context["total_received_coins"] = 0
            context["total_cash_out_coins"] = 0
            context["total_bonus_coins"] = 0
            context["total_from_hots_coins"] = 0
            context["total_from_3days_coins"] = 0

            for coin in context["transfer_coins"]:
                context["total_transferred_coins"] += coin.coins

            for coin in context["received_coins"]:
                context["total_received_coins"] += coin.coins

            for coin in context["cash_out_coins"]:
                context["total_cash_out_coins"] += coin.coins

            for coin in context["bonus_coins"]:
                context["total_bonus_coins"] += coin.coins

            for coin in context["bonus_coins_3days"]:
                context["total_from_3days_coins"] += coin.coins

            context["total_joined_coins"] = (context["total_from_3days_coins"]+context["total_received_coins"] + context["total_bonus_coins"]+context["total_from_hots_coins"]) - (context["total_transferred_coins"] + context["total_cash_out_coins"])

        except CashAndCoinsTable.DoesNotExist or TransferCoins.DoesNotExist or ReceiveCoins.DoesNotExist or HostBuyCash.DoesNotExist or ReceiveCoins3daysOffer.DoesNotExist:
            pass
        context["user"] = request.user

        context["main_domain_address"] = global_domain_name

        usr = User.objects.get(id=request.user.id)
        show_offer_days = (usr.date_joined + timedelta(days=3)) - localtime(now()).date()

        if show_offer_days.days.numerator < 1:
            show_offer_days = 0
        context['offer_day'] = show_offer_days

        offer_days = (request.user.date_joined + timedelta(days=3)) - localtime(now()).date()
        offer_days = offer_days.days.numerator

        # level up function
        i_called = ProfileLevel.objects.filter(
            user__call_by=request.user.id,
            active_with_pay=True,
            user__response_count=True).count()

        response = 1
        for i in range(i_called):
            response += i

        if response < 3:

            for iam in range(response):
                pl = User.objects.filter(
                    response_count=False,
                    payment_done=True,
                    call_by=request.user.id).all()
                for usr in pl:
                    data = User.objects.get(id=usr.id)
                    data.response_count = True
                    data.save()
                    AccountActivationCoins.objects.create(coins=9, send_to=request.user.id)

        if response < 13:

            for iam in range(response):
                pl = User.objects.filter(
                    response_count=False,
                    payment_done=True,
                    call_by=request.user.id).all()
                for usr in pl:
                    data = User.objects.get(id=usr.id)
                    data.response_count = True
                    data.save()
                    AccountActivationCoins.objects.create(coins=10, send_to=request.user.id)

        if response < 43:

            for iam in range(response):
                pl = User.objects.filter(
                    response_count=False,
                    payment_done=True,
                    call_by=request.user.id).all()
                for usr in pl:
                    data = User.objects.get(id=usr.id)
                    data.response_count = True
                    data.save()
                    AccountActivationCoins.objects.create(coins=12, send_to=request.user.id)

        if response < 83:

            for iam in range(response):
                pl = User.objects.filter(
                    response_count=False,
                    payment_done=True,
                    call_by=request.user.id).all()
                for usr in pl:
                    data = User.objects.get(id=usr.id)
                    data.response_count = True
                    data.save()
                    AccountActivationCoins.objects.create(coins=13, send_to=request.user.id)

        if response < 133:
            for iam in range(response):
                pl = User.objects.filter(
                    response_count=False,
                    payment_done=True,
                    call_by=request.user.id).all()
                for usr in pl:
                    data = User.objects.get(id=usr.id)
                    data.response_count = True
                    data.save()
                    AccountActivationCoins.objects.create(coins=15, send_to=request.user.id)

        if response > 134:

            for iam in range(response):
                pl = User.objects.filter(
                    response_count=False,
                    payment_done=True,
                    call_by=request.user.id).all()
                for usr in pl:
                    data = User.objects.get(id=usr.id)
                    data.response_count = True
                    data.save()
                    AccountActivationCoins.objects.create(coins=16, send_to=request.user.id)

        # ----------
        # LEVEL-1
        # ----------
        print(response)
        if (response > 2) and (response < 12):

            if not offer_days < 1:

                profile_level = ProfileLevel.objects.get(user_id=request.user.id)
                profile_level.user_level = 2
                profile_level.save()

                if usr.call_by is None:
                    pass
                else:
                    ReceiveCoins.objects.create(coin=3, receive_by=usr.call_by)
                    TransferCoins.objects.create(coins=3, given_by=request.user.id)

                if not ReceiveCoins3daysOffer.objects.filter(receive_by=request.user.id).exists():
                    ReceiveCoins3daysOffer.objects.create(receive_by=request.user.id, coins=5)
                    try:
                        subject = "Level Up Congrats!"
                        message = f"Hello {request.user.username},\n" \
                                  f"Congrats, You have successfully migrated to Level-2.\n" \
                                  f"You have called in 3 new users within 3 days so you have received 5 coins in bonus."
                        from_email = settings.EMAIL_HOST_USER
                        receiver = [request.user.email, ]
                        send_mail(subject, message, from_email, receiver)
                    except socket.error:
                        messages.error(request, "Server response time out, try again!!",
                                       extra_tags="request_url_sent_error")
            else:
                profile_level = ProfileLevel.objects.get(user_id=request.user.id)
                profile_level.user_level = 2
                profile_level.save()

                if usr.call_by is None:
                    pass
                else:
                    ReceiveCoins.objects.create(coin=3, receive_by=usr.call_by)
                    TransferCoins.objects.create(coins=3, given_by=request.user.id)

                try:
                    subject = "Level Up Congrats!"
                    message = f"Hello {request.user.username},\n" \
                              f"Congrats, You have successfully migrated to Level-2."
                    from_email = settings.EMAIL_HOST_USER
                    receiver = [request.user.email, ]
                    send_mail(subject, message, from_email, receiver)
                except socket.error:
                    messages.error(request, "Server response time out, try again!!",
                                   extra_tags="request_url_sent_error")

        # ---------
        # LEVEL-2
        # ---------
        elif (response > 12) and (response < 42):

            profile_level = ProfileLevel.objects.get(user_id=request.user.id)
            profile_level.user_level = 3
            profile_level.save()

            if usr.call_by is None:
                pass
            else:
                ReceiveCoins.objects.create(coin=5, receive_by=usr.call_by)
                TransferCoins.objects.create(coins=5, given_by=request.user.id)

            try:
                subject = "Level Up Congrats!"
                message = f"Hello {request.user.username},\n" \
                          f"Congrats, You have successfully migrated to Level-3."
                from_email = settings.EMAIL_HOST_USER
                receiver = [request.user.email, ]
                send_mail(subject, message, from_email, receiver)
            except socket.error:
                messages.error(request, "Server response time out, try again!!",
                               extra_tags="request_url_sent_error")

        # ---------
        # LEVEL-3
        # ---------
        elif (response > 42) and (response < 82):

            profile_level = ProfileLevel.objects.get(user_id=request.user.id)
            profile_level.user_level = 4
            profile_level.save()

            if usr.call_by is None:
                pass
            else:
                ReceiveCoins.objects.create(coin=7, receive_by=usr.call_by)
                TransferCoins.objects.create(coins=7, given_by=request.user.id)

            try:
                subject = "Level Up Congrats!"
                message = f"Hello {request.user.username},\n" \
                          f"Congrats, You have successfully migrated to Level-4."
                from_email = settings.EMAIL_HOST_USER
                receiver = [request.user.email, ]
                send_mail(subject, message, from_email, receiver)
            except socket.error:
                messages.error(request, "Server response time out, try again!!",
                               extra_tags="request_url_sent_error")

        # ---------
        # LEVEL-4
        # ---------
        elif (response > 82) and (response < 132):

            profile_level = ProfileLevel.objects.get(user_id=request.user.id)
            profile_level.user_level = 5
            profile_level.save()

            if usr.call_by is None:
                pass
            else:
                ReceiveCoins.objects.create(coin=10, receive_by=usr.call_by)
                TransferCoins.objects.create(coins=10, given_by=request.user.id)

            try:
                subject = "Level Up Congrats!"
                message = f"Hello {request.user.username},\n" \
                          f"Congrats, You have successfully migrated to Level-5."
                from_email = settings.EMAIL_HOST_USER
                receiver = [request.user.email, ]
                send_mail(subject, message, from_email, receiver)
            except socket.error:
                messages.error(request, "Server response time out, try again!!",
                               extra_tags="request_url_sent_error")

        # ---------
        # LEVEL-5
        # ---------
        elif response > 132:

            profile_level = ProfileLevel.objects.get(user_id=request.user.id)
            profile_level.user_level = 6
            profile_level.save()

            if usr.call_by is None:
                pass
            else:
                ReceiveCoins.objects.create(coin=12, receive_by=usr.call_by)
                TransferCoins.objects.create(coins=12, given_by=request.user.id)

            try:
                subject = "Level Up Congrats!"
                message = f"Hello {request.user.username},\n" \
                          f"Congrats, You have successfully migrated to Level-6."
                from_email = settings.EMAIL_HOST_USER
                receiver = [request.user.email, ]
                send_mail(subject, message, from_email, receiver)
            except socket.error:
                messages.error(request, "Server response time out, try again!!",
                               extra_tags="request_url_sent_error")

        return render(request, self.template_name, context)


# ---------------------------------------------------------------
# profile leader board from profile
# ---------------------------------------------------------------
class UserLeaderBoard(View):

    template_name = "frontend/user_views/leader-board.html"

    def get(self, request):
        context = {}
        try:
            context["user_level"] = ProfileLevel.objects.get(user=request.user)
        except ProfileLevel.DoesNotExist:
            pass
        context["user"] = request.user
        try:
            context['leader_board_winner'] = PersonCounter.objects.all().order_by('refers')
        except PersonCounter.DoesNotExist:
            pass
        return render(request, self.template_name, context)


# ---------------------------------------------------------------
# User tree data from profile
# ---------------------------------------------------------------
class UserTree(View):

    template_name = "frontend/user_views/tree.html"

    def get(self, request):
        context = {}
        context["user"] = request.user
        try:
            context["self_level"] = ProfileLevel.objects.get(user_id=request.user.id)
            context["user_level"] = ProfileLevel.objects.get(user=request.user)
            if context["self_level"].user_level == 1:
                context["tree_data"] = ProfileLevel.objects.filter(active_with_pay=True,
                                                               user__call_by=request.user.id).order_by("-id").all()
        except ProfileLevel.DoesNotExist:
            pass

        return render(request, self.template_name, context)


# ---------------------------------------------------------------
# User wallet from profile
# ---------------------------------------------------------------
class UserWallet(View):

    template_name = "frontend/user_views/wallet.html"

    def get(self, request):
        context = {}
        try:
            context["user_level"] = ProfileLevel.objects.get(user=request.user)
            amount = 0
            if context["user_level"].pay_by_user == 0:
                amount = 1800
            if context["user_level"].pay_by_user == 1800:
                amount = 100
            if context["user_level"].pay_by_user == 100:
                amount = 500
            if context["user_level"].pay_by_user == 500:
                amount = 700
            if context["user_level"].pay_by_user == 700:
                amount = 1000
            if context["user_level"].pay_by_user == 1000:
                amount = 1200
            context["buy_coin_form"] = BuyCoinsForm(initial={
                "bdt": amount
            })
        except ProfileLevel.DoesNotExist:
            pass
        context["user"] = request.user
        try:
            context["coins"] = CashAndCoinsTable.objects.filter(user=request.user).all()
            context["total_coin"] = 0
            for coin in context["coins"]:
                context["total_coin"] += coin.user_coins
        except CashAndCoinsTable.DoesNotExist:
            pass
        context["coin_transfer_form"] = TransferCoinsForm()
        try:
            context["transfer_coins"] = TransferCoins.objects.filter(given_by=request.user.id).all()
            context["received_coins"] = ReceiveCoins.objects.filter(receive_by=request.user.id).all()
            context["cash_out_coins"] = CashOutRequestTable.objects.filter(ask_by=request.user.id).all()
            context["bonus_coins"] = AccountActivationCoins.objects.filter(send_to=request.user.id).all()
            context["bonus_coins_fh"] = HostBuyCash.objects.filter(send_to=request.user.id, approve=True).all()
            context["bonus_coins_3days"] = ReceiveCoins3daysOffer.objects.filter(receive_by=request.user.id).all()

            context["total_transferred_coins"] = 0
            context["total_received_coins"] = 0
            context["total_cash_out_coins"] = 0
            context["total_bonus_coins"] = 0
            context["total_from_hots_coins"] = 0
            context["total_from_3days_coins"] = 0

            for coin in context["transfer_coins"]:
                context["total_transferred_coins"] += coin.coins

            for coin in context["received_coins"]:
                context["total_received_coins"] += coin.coins

            for coin in context["cash_out_coins"]:
                context["total_cash_out_coins"] += coin.coins

            for coin in context["bonus_coins"]:
                context["total_bonus_coins"] += coin.coins

            for coin in context["bonus_coins_3days"]:
                context["total_from_3days_coins"] += coin.coins

            context["total_joined_coins"] = (context["total_from_3days_coins"] + context["total_received_coins"] +
                                             context["total_bonus_coins"] + context["total_from_hots_coins"]) - (
                                                        context["total_transferred_coins"] + context[
                                                    "total_cash_out_coins"])

        except CashAndCoinsTable.DoesNotExist or TransferCoins.DoesNotExist or ReceiveCoins.DoesNotExist or HostBuyCash.DoesNotExist or ReceiveCoins3daysOffer.DoesNotExist:
            pass
        context["cash_out_form"] = CashOutForm()
        context["host_buy_form"] = HostBuyCoins()
        return render(request, self.template_name, context)

    def post(self, request):

        context = {}
        context["user_level"] = ProfileLevel.objects.get(user=request.user)
        context["user"] = request.user
        amount = 0

        # ---------------------------------------------------------------
        # Coins calculation algorithm
        # ---------------------------------------------------------------
        try:
            context["transfer_coins"] = TransferCoins.objects.filter(given_by=request.user.id).all()
            context["received_coins"] = ReceiveCoins.objects.filter(receive_by=request.user.id).all()
            context["cash_out_coins"] = CashOutRequestTable.objects.filter(ask_by=request.user.id).all()
            context["bonus_coins"] = AccountActivationCoins.objects.filter(send_to=request.user.id).all()
            context["bonus_coins_fh"] = HostBuyCash.objects.filter(send_to=request.user.id, approve=True).all()
            context["bonus_coins_3days"] = ReceiveCoins3daysOffer.objects.filter(receive_by=request.user.id).all()

            context["total_transferred_coins"] = 0
            context["total_received_coins"] = 0
            context["total_cash_out_coins"] = 0
            context["total_bonus_coins"] = 0
            context["total_from_hots_coins"] = 0
            context["total_from_3days_coins"] = 0

            for coin in context["transfer_coins"]:
                context["total_transferred_coins"] += coin.coins

            for coin in context["received_coins"]:
                context["total_received_coins"] += coin.coins

            for coin in context["cash_out_coins"]:
                context["total_cash_out_coins"] += coin.coins

            for coin in context["bonus_coins"]:
                context["total_bonus_coins"] += coin.coins

            for coin in context["bonus_coins_3days"]:
                context["total_from_3days_coins"] += coin.coins

            context["total_joined_coins"] = (context["total_from_3days_coins"] + context["total_received_coins"] +
                                             context["total_bonus_coins"] + context["total_from_hots_coins"]) - (
                                                        context["total_transferred_coins"] + context[
                                                    "total_cash_out_coins"])

        except CashAndCoinsTable.DoesNotExist or TransferCoins.DoesNotExist or ReceiveCoins.DoesNotExist or HostBuyCash.DoesNotExist or ReceiveCoins3daysOffer.DoesNotExist:
            pass

        # ---------------------------------------------------------------
        # pay money section from wallet
        # ---------------------------------------------------------------
        if "pay_money" in request.POST:
            if context["user_level"].pay_by_user == 0:
                amount = 1800
            if context["user_level"].pay_by_user == 1800:
                amount = 100
            if context["user_level"].pay_by_user == 100:
                amount = 500
            if context["user_level"].pay_by_user == 500:
                amount = 700
            if context["user_level"].pay_by_user == 700:
                amount = 1000
            if context["user_level"].pay_by_user == 1000:
                amount = 1200
            context["buy_coin_form"] = BuyCoinsForm(request.POST, initial={
                "bdt": amount
            })
            context["cash_out_form"] = CashOutForm()
            context["coin_transfer_form"] = TransferCoinsForm()

            if context["buy_coin_form"].is_valid():
                context["user_level"].pay_by_user = context["buy_coin_form"].cleaned_data.get("bdt", None)
                context["user_level"].transaction_id = context["buy_coin_form"].cleaned_data.get("transaction_id", None)
                context["user_level"].has_paid = True
                context["user_level"].review = False
                context["user_level"].save()
                messages.success(request, "Your payment is under review, get back to you soon!",
                                 extra_tags="review_message")
                return redirect("user_profile")

        # ---------------------------------------------------------------
        # Transfer money section from wallet
        # ---------------------------------------------------------------
        if "transfer_coins" in request.POST:
            context["buy_coin_form"] = BuyCoinsForm(initial={
                "bdt": amount
            })
            context["coin_transfer_form"] = TransferCoinsForm(request.POST)
            if context["coin_transfer_form"].is_valid():

                coins = context["coin_transfer_form"].cleaned_data.get("coins", None)
                to_id = context["coin_transfer_form"].cleaned_data.get("to_id", None)

                try:
                    context["transfer_coins"] = TransferCoins.objects.filter(given_by=request.user.id).all()
                    context["received_coins"] = ReceiveCoins.objects.filter(receive_by=request.user.id).all()
                    context["cash_out_coins"] = CashOutRequestTable.objects.filter(ask_by=request.user.id).all()
                    context["bonus_coins"] = AccountActivationCoins.objects.filter(send_to=request.user.id).all()
                    context["bonus_coins_fh"] = HostBuyCash.objects.filter(send_to=request.user.id, approve=True).all()
                    context["bonus_coins_3days"] = ReceiveCoins3daysOffer.objects.filter(
                        receive_by=request.user.id).all()

                    context["total_transferred_coins"] = 0
                    context["total_received_coins"] = 0
                    context["total_cash_out_coins"] = 0
                    context["total_bonus_coins"] = 0
                    context["total_from_hots_coins"] = 0
                    context["total_from_3days_coins"] = 0

                    for coin in context["transfer_coins"]:
                        context["total_transferred_coins"] += coin.coins

                    for coin in context["received_coins"]:
                        context["total_received_coins"] += coin.coins

                    for coin in context["cash_out_coins"]:
                        context["total_cash_out_coins"] += coin.coins

                    for coin in context["bonus_coins"]:
                        context["total_bonus_coins"] += coin.coins

                    for coin in context["bonus_coins_3days"]:
                        context["total_from_3days_coins"] += coin.coins

                    context["total_joined_coins"] = (context["total_from_3days_coins"] + context[
                        "total_received_coins"] + context["total_bonus_coins"] + context["total_from_hots_coins"]) - (
                                                                context["total_transferred_coins"] + context[
                                                            "total_cash_out_coins"])
                    if int(coins) < 0:
                        context["transfer_error"] = "Must not be less than 1 coins!"
                        return render(request, self.template_name, context)
                    elif int(context["total_joined_coins"]) < int(coins):
                        context["transfer_error"] = "You don't have enough balance!"
                        return render(request, self.template_name, context)
                    else:
                        if int(context["user_level"].user_level) > 0:
                            if User.objects.filter(id=to_id).exists():
                                TransferCoins.objects.create(coins=coins, given_by=request.user.id)
                                ReceiveCoins.objects.create(coins=coins, receive_by=to_id)
                                try:
                                    user = User.objects.get(id=to_id)
                                    subject = "Transferred Coins"
                                    message = f"Hello {user.username}\n" \
                                              f"You have received {coins} Coins from {request.user.username}"
                                    from_email = settings.EMAIL_HOST_USER
                                    receiver = [user.email, ]
                                    send_mail(subject, message, from_email, receiver)
                                    messages.success(request,
                                                     "You have successfully transferred coins!",
                                                     extra_tags="transfer_success")
                                    return redirect('wallet')
                                except socket.error:
                                    messages.error(request, "Server response time out, try again!!",
                                                   extra_tags="request_url_sent_error")
                                return redirect('user_profile')
                            else:
                                context["transfer_error"] = "Web could not find such ID you are looking for!"
                                return render(request, self.template_name, context)
                        else:
                            context["transfer_error"] = "Upgrade level to share coins!!"
                            return render(request, self.template_name, context)
                except CashAndCoinsTable.DoesNotExist or TransferCoins.DoesNotExist or ReceiveCoins.DoesNotExist or HostBuyCash.DoesNotExist or ReceiveCoins3daysOffer.DoesNotExist:
                    pass

        # ---------------------------------------------------------------
        # cash out money section from wallet
        # ---------------------------------------------------------------
        if "cash_out" in request.POST:
            context["buy_coin_form"] = BuyCoinsForm(initial={
                "bdt": amount
            })
            context["coin_transfer_form"] = TransferCoinsForm()
            context["cash_out_form"] = CashOutForm(request.POST)

            if context["cash_out_form"].is_valid():

                request_coins = context["cash_out_form"].cleaned_data.get("coins", None)
                number = context["cash_out_form"].cleaned_data.get("number", None)

                try:
                    context["transfer_coins"] = TransferCoins.objects.filter(given_by=request.user.id).all()
                    context["received_coins"] = ReceiveCoins.objects.filter(receive_by=request.user.id).all()
                    context["cash_out_coins"] = CashOutRequestTable.objects.filter(ask_by=request.user.id).all()
                    context["bonus_coins"] = AccountActivationCoins.objects.filter(send_to=request.user.id).all()
                    context["bonus_coins_fh"] = HostBuyCash.objects.filter(send_to=request.user.id, approve=True).all()
                    context["bonus_coins_3days"] = ReceiveCoins3daysOffer.objects.filter(
                        receive_by=request.user.id).all()

                    context["total_transferred_coins"] = 0
                    context["total_received_coins"] = 0
                    context["total_cash_out_coins"] = 0
                    context["total_bonus_coins"] = 0
                    context["total_from_hots_coins"] = 0
                    context["total_from_3days_coins"] = 0

                    for coin in context["transfer_coins"]:
                        context["total_transferred_coins"] += coin.coins

                    for coin in context["received_coins"]:
                        context["total_received_coins"] += coin.coins

                    for coin in context["cash_out_coins"]:
                        context["total_cash_out_coins"] += coin.coins

                    for coin in context["bonus_coins"]:
                        context["total_bonus_coins"] += coin.coins

                    for coin in context["bonus_coins_3days"]:
                        context["total_from_3days_coins"] += coin.coins

                    context["total_joined_coins"] = (context["total_from_3days_coins"] + context[
                        "total_received_coins"] + context["total_bonus_coins"] + context["total_from_hots_coins"]) - (
                                                                context["total_transferred_coins"] + context[
                                                            "total_cash_out_coins"])
                    if int(request_coins) < 1:
                        context["cash_out_error"] = "Must not be less than 1 coins!"
                        return render(request, self.template_name, context)
                    elif int(context["total_joined_coins"]) < int(request_coins):
                        context["cash_out_error"] = "You don't have enough balance to withdraw!"
                        return render(request, self.template_name, context)
                    else:
                        if context["user_level"].user_level > 0:
                            if not CashOutRequestTable.objects.filter(ask_date=date.today(),
                                                                      ask_by=request.user).exists():
                                cash = int(request_coins) * 100
                                CashOutRequestTable.objects.create(coins=request_coins,
                                                                   number=number, ask_by=request.user, cash=cash)
                                try:
                                    subject = "Requested Cash Out From KashBytes"
                                    message = f"Hello {request.user.username}\n" \
                                              f"You have requested to cash out for {request_coins} Coins = {cash} BDT.\n" \
                                              f"We will respond you shortly!"
                                    from_email = settings.EMAIL_HOST_USER
                                    receiver = [request.user.email, ]
                                    send_mail(subject, message, from_email, receiver)

                                    messages.success(request, "Request is under review!, We will send you cash soon!\n"
                                                              "Thank you.",
                                                     extra_tags="cash_out_success")
                                except socket.error:
                                    messages.error(request, "Server response time out, try again!!",
                                                   extra_tags="request_url_sent_error")
                            else:
                                context["same_date_error"] = "Sorry! You can't request for multiple time in a day!"
                                return render(request, self.template_name, context)
                        else:
                            context["same_date_error"] = "Upgrade level to withdraw coins!!"
                            return render(request, self.template_name, context)
                        return redirect('wallet')
                except CashAndCoinsTable.DoesNotExist or TransferCoins.DoesNotExist or ReceiveCoins.DoesNotExist or HostBuyCash.DoesNotExist or ReceiveCoins3daysOffer.DoesNotExist:
                    pass

        # ---------------------------------------------------------------
        # buy coins from host section from wallet
        # ---------------------------------------------------------------
        if "buy_coins_from_host" in request.POST:
            context["buy_coin_form"] = BuyCoinsForm(initial={
                "bdt": amount
            })
            context["coin_transfer_form"] = TransferCoinsForm()
            context["cash_out_form"] = CashOutForm()
            context["host_buy_form"] = HostBuyCoins(request.POST)

            if context["host_buy_form"].is_valid():

                bdt = context["host_buy_form"].cleaned_data.get("bdt", None)
                transaction_id = context["host_buy_form"].cleaned_data.get("transaction_id", None)

                try:
                    context["transfer_coins"] = TransferCoins.objects.filter(given_by=request.user.id).all()
                    context["received_coins"] = ReceiveCoins.objects.filter(receive_by=request.user.id).all()
                    context["cash_out_coins"] = CashOutRequestTable.objects.filter(ask_by=request.user.id).all()
                    context["bonus_coins"] = AccountActivationCoins.objects.filter(send_to=request.user.id).all()
                    context["bonus_coins_fh"] = HostBuyCash.objects.filter(send_to=request.user.id, approve=True).all()
                    context["bonus_coins_3days"] = ReceiveCoins3daysOffer.objects.filter(
                        receive_by=request.user.id).all()

                    context["total_transferred_coins"] = 0
                    context["total_received_coins"] = 0
                    context["total_cash_out_coins"] = 0
                    context["total_bonus_coins"] = 0
                    context["total_from_hots_coins"] = 0
                    context["total_from_3days_coins"] = 0

                    for coin in context["transfer_coins"]:
                        context["total_transferred_coins"] += coin.coins

                    for coin in context["received_coins"]:
                        context["total_received_coins"] += coin.coins

                    for coin in context["cash_out_coins"]:
                        context["total_cash_out_coins"] += coin.coins

                    for coin in context["bonus_coins"]:
                        context["total_bonus_coins"] += coin.coins

                    for coin in context["bonus_coins_3days"]:
                        context["total_from_3days_coins"] += coin.coins

                    context["total_joined_coins"] = (context["total_from_3days_coins"] + context[
                        "total_received_coins"] + context["total_bonus_coins"] + context["total_from_hots_coins"]) - (
                                                                context["total_transferred_coins"] + context[
                                                            "total_cash_out_coins"])
                    coins = int(bdt)/100
                    HostBuyCash.objects.create(
                        cash=bdt,
                        coins=coins,
                        send_to=request.user.id,
                        transaction_id=transaction_id
                    )
                    messages.success(request, "We have got your request, coins will be added if transaction id matched. Thank you.", extra_tags="host_cash_buy_success")
                    return redirect("user_profile")
                except CashAndCoinsTable.DoesNotExist or TransferCoins.DoesNotExist or ReceiveCoins.DoesNotExist or HostBuyCash.DoesNotExist or ReceiveCoins3daysOffer.DoesNotExist:
                    pass
        return render(request, self.template_name, context)
