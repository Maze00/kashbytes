from django import forms
import re
from django.contrib.auth import get_user_model

User = get_user_model()


# ---------------------------------------------------------------
# Request referral form to request url from website
# ---------------------------------------------------------------
class RequestReferralForm(forms.Form):

    email_address = forms.EmailField(
        label="Enter Your Email To Get The Referral Link",
        widget=forms.TextInput(attrs={
            "placeholder": "yourmail@mail.com"
        })
    )

    def clean_email_address(self):
        email_address = self.cleaned_data.get("email_address", None)
        if email_address == "":
            raise forms.ValidationError("Email address is required!")
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email_address):
            raise forms.ValidationError("Invalid email format!")
        return email_address


# ---------------------------------------------------------------
# User registration form for register new user
# ---------------------------------------------------------------
class RegistrationForm(forms.Form):

    username = forms.CharField(max_length=30, label="Username", required=False)
    email = forms.EmailField(max_length=30, label="E-mail", required=False)
    password = forms.CharField(
        max_length=50,
        label="Password",
        widget=forms.PasswordInput(attrs={"onkeyup": "check();", "id": "password"})
    )
    confirm_password = forms.CharField(
        max_length=50,
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"onkeyup": "check();", "id": "confirm_password"})
    )
    mobile_number = forms.CharField(max_length=15, label="Mobile Number", required=False)
    date_of_birth = forms.CharField(
        label="Date of Birth",
        widget=forms.TextInput(attrs={"type": "date"})
    )
    CHOICES = (
        ('', '-- Select Gender --'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Others'),
    )
    gender = forms.CharField(
        max_length=12,
        label="Gender",
        widget=forms.Select(choices=CHOICES)
    )
    agreement = forms.CharField(required=False, widget=forms.CheckboxInput)

    def clean_username(self):
        username = self.cleaned_data.get("username", None)
        if username == "":
            raise forms.ValidationError("Username is required!")
        if not re.match(r"^[[A-Z]|[a-z]][[A-Z]|[a-z]|\\d|[_]]{7,29}$", username):
            raise forms.ValidationError("Invalid username format")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is taken, please try another!")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", None)
        if email == "":
            raise forms.ValidationError("E-mail is required!")
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            raise forms.ValidationError("Invalid username format")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered!")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password", None)
        if password == "":
            raise forms.ValidationError("Password is required!")
        if len(password) < 8:
            raise forms.ValidationError("Shouldn't be less than 8 chars!")
        return password

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data.get("confirm_password", None)
        if confirm_password == "":
            raise forms.ValidationError("Password is required!")
        if len(confirm_password) < 8:
            raise forms.ValidationError("Shouldn't be less than 8 chars!")
        return confirm_password

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password", None)
        confirm_password = cleaned_data.get("confirm_password", None)

        if password != confirm_password:
            raise forms.ValidationError("Confirm password is not same to password!")

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get("mobile_number", None)
        if mobile_number == "":
            raise forms.ValidationError("Mobile number is required!")
        if not mobile_number.isnumeric():
            raise forms.ValidationError("Invalid mobile number format!")
        if len(mobile_number) != 11:
            raise forms.ValidationError("Original number required!")
        return mobile_number

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get("date_of_birth", None)
        if date_of_birth == "":
            raise forms.ValidationError("Date of birth is required!")
        return date_of_birth

    def clean_gender(self):
        gender = self.cleaned_data.get("gender", None)
        if gender == "":
            raise forms.ValidationError("Gender selection is required!")
        return gender

    def clean_agreement(self):
        agreement = self.cleaned_data.get("agreement", None)
        if "True" not in agreement:
            raise forms.ValidationError("Do you not agree with our TOS?")
        return agreement


# ---------------------------------------------------------------
# User login form top login user
# ---------------------------------------------------------------
class UserLoginForm(forms.Form):

    user = forms.CharField(
        label="Username/Email",
        widget=forms.TextInput()
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput()
    )

    def clean_user(self):
        user = self.cleaned_data.get('user', None)
        if user.__eq__(""):
            msg = "Username / E-mail is required!"
            raise forms.ValidationError(msg)
        return user

    def clean_password(self):
        password = self.cleaned_data.get('password', None)
        if password.__eq__(""):
            msg = "Admin password is required!"
            raise forms.ValidationError(msg)
        return password


# ---------------------------------------------------------------
# Buy coin form for buying coins from author
# ---------------------------------------------------------------
class BuyCoinsForm(forms.Form):

    bdt = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "BDT"}),
        disabled=True
    )

    transaction_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Transaction I.D"}),
    )

    def clean_transaction_id(self):
        tid = self.cleaned_data.get("transaction_id", None)
        if tid == "":
            raise forms.ValidationError("Transaction ID is required!")
        return tid


# ---------------------------------------------------------------
# Forgot password form
# ---------------------------------------------------------------
class ForgotPasswordForm(forms.Form):

    email = forms.EmailField(
        label="Email",
        required=False,
        max_length=30
    )

    def clean_email(self):
        email = self.cleaned_data.get("email", None)
        if email == "":
            raise forms.ValidationError("E-mail is required!")
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            raise forms.ValidationError("Invalid username format")
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email not found in record!")
        return email


# ---------------------------------------------------------------
# Change password form
# ---------------------------------------------------------------
class ChangePasswordForm(forms.Form):

    password = forms.CharField(
        label="New Password",
        max_length=50,
        widget=forms.PasswordInput(attrs={"onkeyup": "check2();", "id": "password"}),
        required=False
    )
    confirm_password = forms.CharField(
        max_length=50,
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"onkeyup": "check2();", "id": "confirm_password"}),
        required=False
    )

    def clean_password(self):
        password = self.cleaned_data.get("password", None)
        if password == "":
            raise forms.ValidationError("Password is required!")
        if len(password) < 8:
            raise forms.ValidationError("Shouldn't be less than 8 chars!")
        return password

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data.get("confirm_password", None)
        if confirm_password == "":
            raise forms.ValidationError("Confirm password is required!")
        if len(confirm_password) < 8:
            raise forms.ValidationError("Shouldn't be less than 8 chars!")
        return confirm_password

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        password = cleaned_data.get("password", None)
        confirm_password = cleaned_data.get("confirm_password", None)

        if password != confirm_password:
            raise forms.ValidationError("Confirm password is not same to password!")


# ---------------------------------------------------------------
# Transfer coins form to transfer coins to another user
# ---------------------------------------------------------------
class TransferCoinsForm(forms.Form):
    coins = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Coins", "class": "formsecond"})
    )

    to_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "I.D no."})
    )

    def clean_coins(self):
        coins = self.cleaned_data.get("coins", None)
        if coins == "":
            raise forms.ValidationError("Coins is required!")
        if not coins.isnumeric():
            raise forms.ValidationError("Invalid coin format!")
        return coins

    def clean_to_id(self):
        to_id = self.cleaned_data.get("to_id", None)
        if to_id == "":
            raise forms.ValidationError("I.D No. is required!")
        if not to_id.isnumeric():
            raise forms.ValidationError("Invalid user format!")
        return to_id


# ---------------------------------------------------------------
# Cash out form to cash out from wallet
# ---------------------------------------------------------------
class CashOutForm(forms.Form):
    coins = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "coins"})
    )

    number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "01*********"})
    )

    def clean_coins(self):
        coins = self.cleaned_data.get("coins", None)
        if coins == "":
            raise forms.ValidationError("Coins is required!")
        if not coins.isnumeric():
            raise forms.ValidationError("Invalid coin format!")
        if int(coins) < 0:
            raise forms.ValidationError("Not allowed!")
        return coins

    def clean_number(self):
        number = self.cleaned_data.get("number", None)
        if number == "":
            raise forms.ValidationError("Mobile number required!")
        if len(number) != 11:
            raise forms.ValidationError("Original number required!")
        return number


# ---------------------------------------------------------------
# Buy coins form from host
# ---------------------------------------------------------------
class HostBuyCoins(forms.Form):
    bdt = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "BDT"})
    )

    transaction_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"Placeholder": "Transaction Id"})
    )

    def clean_bdt(self):
        bdt = self.cleaned_data.get("bdt", None)
        if bdt == "":
            raise forms.ValidationError("Cash is required!")
        if not bdt.isnumeric():
            raise forms.ValidationError("Invalid cash format!")
        if int(bdt) < 0:
            raise forms.ValidationError("Not allowed!")

        if (int(bdt) % 100) != 0:
            raise forms.ValidationError("Note: 100BDT = 1 Coins!")
        return bdt

    def clean_transaction_id(self):
        transaction_id = self.cleaned_data.get("transaction_id", None)
        if transaction_id == "":
            raise forms.ValidationError("Transaction id required!")
        return transaction_id
