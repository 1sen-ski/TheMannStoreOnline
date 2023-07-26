from django import forms
from django.contrib.auth.models import User
from . import models
from .models import Customer
from .validators import validate_name, validate_username, validate_password, validate_password_numbers, validate_mobile, \
    validate_mobile_for_payment, validate_card_number, validate_expiry_date, validate_cv_code


# for user
class CustomerUserForm(forms.ModelForm):
    first_name = forms.CharField(validators=[validate_name])
    last_name = forms.CharField(validators=[validate_name])
    username = forms.CharField(validators=[validate_username])
    password = forms.CharField(widget=forms.PasswordInput, validators=[validate_password, validate_password_numbers])

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']


# for user again, kinda split in 2 parts
class CustomerForm(forms.ModelForm):
    mobile = forms.CharField(validators=[validate_mobile])

    class Meta:
        model = Customer
        fields = ['address', 'mobile', 'profile_pic']


# the product form for the admin which he creates in the admin site(not the django admin), the custom admin
class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['name', 'price', 'description', 'product_image']


# address of fake shipment
class AddressForm(forms.Form):
    Email = forms.EmailField()
    Mobile = forms.CharField(validators=[validate_mobile_for_payment])
    Address = forms.CharField(max_length=500)


class PaymentForm(forms.Form):
    CardNumber = forms.CharField(max_length=16, validators=[validate_card_number])

    ExpiryDate = forms.ChoiceField(choices=[
        (f"{str(i).zfill(2)} - {str(j).zfill(2)}", f"{str(i).zfill(2)} - {str(j).zfill(2)}")
        for i in range(1, 13)
        for j in range(22, 30)
    ], validators=[validate_expiry_date])

    CVCode = forms.CharField(min_length=3, max_length=3, validators=[validate_cv_code])


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = models.Feedback
        fields = ['name', 'feedback']


# for updating status of order
class OrderForm(forms.ModelForm):
    class Meta:
        model = models.Orders
        fields = ['status']


# # for contact us page
# class ContactusForm(forms.Form):
#     Name = forms.CharField(max_length=30)
#     Email = forms.EmailField()
#     Message = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))
