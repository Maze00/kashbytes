from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.timezone import localtime, now


# ---------------------------------------------------------------
# Create superuser user function
# ---------------------------------------------------------------
class UsersManager(BaseUserManager):

    def create_superuser(self, email, username, password):

        if not email:
            raise ValueError("E-mail is required!")
        if not username:
            raise ValueError("Username is required!")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.is_superuser = True
        user.is_staff = True

        user.set_password(password)
        user.save(using=self._db)

        ProfileLevel.objects.create(user=user)
        return user


# ---------------------------------------------------------------
# Custom user model
# ---------------------------------------------------------------
class User(AbstractBaseUser):

    email = models.EmailField(verbose_name="email", max_length=30, unique=True)
    username = models.CharField(max_length=30, unique=True)
    last_login = models.DateField(verbose_name="last login", auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=12, null=True, blank=True)
    call_by = models.IntegerField(null=True, blank=True)
    date_joined = models.DateField(default=localtime(now()).date())
    response_count = models.BooleanField(default=False)
    payment_done = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UsersManager()


# ---------------------------------------------------------------
# This table will have referral url id
# ---------------------------------------------------------------
class ReferralUrl(models.Model):

    url_address = models.TextField(max_length=250)
    url_validity = models.BooleanField(default=0)
    self_register = models.BooleanField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "refer_url_table"


# ---------------------------------------------------------------
# Model for calculating user level coins and cash
# ---------------------------------------------------------------
class ProfileLevel(models.Model):
    pay_by_user = models.IntegerField(default=0)
    coins = models.IntegerField(default=0)
    user_level = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    review = models.BooleanField(default=0)
    transaction_id = models.CharField(max_length=250, null=True, blank=True)
    has_paid = models.BooleanField(default=0)
    active_with_pay = models.BooleanField(default=False)

    class Meta:
        db_table = "profile_level"


# ---------------------------------------------------------------
# This model will help to assist in leader board that brings user
# ---------------------------------------------------------------
class PersonCounter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    refers = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "person_counter"


# ---------------------------------------------------------------
# this table will keep all pay money history for Profile Level
# ---------------------------------------------------------------
class CashAndCoinsTable(models.Model):
    user_cash = models.IntegerField()
    user_coins = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cash_and_coins_table'


# ---------------------------------------------------------------
# This model will helps to calculate transfer coins data and who
# wants to transfer the coins
# ---------------------------------------------------------------
class TransferCoins(models.Model):
    coins = models.IntegerField()
    given_by = models.IntegerField()
    transfer_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transfer_coins"


# ---------------------------------------------------------------
# This table will helps to store receive coins for users
# ---------------------------------------------------------------
class ReceiveCoins(models.Model):
    coins = models.IntegerField()
    receive_by = models.IntegerField()
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "received_coins"


# ---------------------------------------------------------------
# This table will helps to store receive coins for 3 days offer
# ---------------------------------------------------------------
class ReceiveCoins3daysOffer(models.Model):
    coins = models.IntegerField()
    receive_by = models.IntegerField()
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "received_coins_3_days"


# ---------------------------------------------------------------
# This table will store password recovery data
# ---------------------------------------------------------------
class PasswordRecoveryUrl(models.Model):
    url = models.CharField(max_length=200)
    validity = models.NullBooleanField(default=0)
    created_at = models.DateField()
    updated_at = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "password_recovery_field"


# ---------------------------------------------------------------
# This table will assist to keep calculation for cash out data
# ---------------------------------------------------------------
class CashOutRequestTable(models.Model):
    coins = models.IntegerField()
    cash = models.IntegerField()
    number = models.CharField(max_length=11)
    ask_date = models.DateField(auto_now_add=True)
    is_done = models.BooleanField(default=False)
    is_approve = models.BooleanField(null=True, blank=True)
    ask_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "cash_out_request_table"


# ---------------------------------------------------------------
# When an account will be activated user will  paid coins
# ---------------------------------------------------------------
class AccountActivationCoins(models.Model):
    coins = models.IntegerField()
    activation_date = models.DateField(auto_now_add=True)
    send_to = models.IntegerField()

    class Meta:
        db_table = "account_activation_coins_table"


# ---------------------------------------------------------------
# This model will keep data from buy coins from host
# ---------------------------------------------------------------
class HostBuyCash(models.Model):
    cash = models.IntegerField()
    coins = models.IntegerField(default=0)
    transaction_id = models.TextField()
    send_to = models.IntegerField()
    approve = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)
    activation_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "host_buy_cash"
