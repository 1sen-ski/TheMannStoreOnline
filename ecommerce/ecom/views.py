from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from . import forms, models
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from .forms import PaymentForm, AddressForm


# 1st help-up function
# This function is present alot in the views. If it's not in the view, the cart items don't show up.
def get_product_count_in_cart(request):
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0
    return product_count_in_cart


# 2nd help-up function
def calculate_total_from_cookies(request):
    total = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart = product_ids.split('|')
            products = models.Product.objects.filter(id__in=product_id_in_cart)
            for p in products:
                total += p.price
    return total


# 3rd help-up function
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()


# 4th help-up function
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()


# 5th help-up function
def is_staff(user):
    return user.groups.filter(name='STAFF').exists()


# 6th help-up function
def is_admin_or_staff(user):
    return is_admin(user) or is_staff(user)


# 7th help-up function
def get_ordered_items():
    orders = models.Orders.objects.all().select_related('product', 'customer')
    ordered_items = []
    for order in orders:
        ordered_product = order.product
        ordered_customer = order.customer
        ordered_items.append((ordered_product, ordered_customer, order))

    return ordered_items


class IndexView(TemplateView):
    template_name = 'common/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = models.Product.objects.all()
        context['product_count_in_cart'] = get_product_count_in_cart(self.request)
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('after_login')
        return super().dispatch(request, *args, **kwargs)


# for showing login button for admin
def admin_click_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('after_login')
    return HttpResponseRedirect('admin_login')


def customer_signup_view(request):
    if request.method == 'POST':
        user_form = forms.CustomerUserForm(request.POST)
        customer_form = forms.CustomerForm(request.POST, request.FILES)

        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()

            customer = customer_form.save(commit=False)
            customer.user = user
            customer.save()

            # Our new user becomes CUSTOMER
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)

            return redirect('customer_login')
        else:
            pass

    else:
        user_form = forms.CustomerUserForm()
        customer_form = forms.CustomerForm()

    product_count_in_cart = get_product_count_in_cart(request)
    mydict = {'user_form': user_form, 'customer_form': customer_form, 'product_count_in_cart': product_count_in_cart}
    return render(request, 'customer/customer_signup.html', context=mydict)


class CustomLoginView(LoginView):
    template_name = 'customer/customer_login.html'
    authentication_form = AuthenticationForm

    def form_invalid(self, form):
        # There is a better way to make the errors, but decided that anyway.
        form.add_error('username', 'Invalid username.')
        form.add_error('password', 'Invalid password.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_count_in_cart'] = get_product_count_in_cart(self.request)
        return context


# After the random user logins, he goes to the site home. If it's an admin he goes to the hidden admin site.
# In the signup view every user becomes CUSTOMER, so he cannot possibly enter the admin part
def after_login_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')


class CustomLogoutView(LogoutView):
    template_name = 'common/logout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_count_in_cart'] = get_product_count_in_cart(self.request)
        return context


# ---------------------------------------------------------------------------
# ------------------------ ADMIN RELATED VIEWS ------------------------------
# ---------------------------------------------------------------------------

class Custom_Admin_LoginView(LoginView):
    template_name = 'admin/admin_login.html'
    authentication_form = AuthenticationForm

    def form_invalid(self, form):
        # Add custom error messages to the form fields
        form.add_error('username', 'Invalid username.')
        form.add_error('password', 'Invalid password.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_count_in_cart'] = get_product_count_in_cart(self.request)
        return context


@login_required(login_url='admin_login')
@user_passes_test(is_admin_or_staff)
def admin_dashboard_view(request):
    # for cards on dashboard
    customer_count = models.Customer.objects.all().count()
    product_count = models.Product.objects.all().count()
    order_count = models.Orders.objects.all().count()

    # for recent order tables
    ordered_items = get_ordered_items()

    mydict = {
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
        'data': ordered_items,
    }
    return render(request, 'admin/admin_dashboard.html', context=mydict)


# admin view customer table
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def view_customer_view(request):
    customers = models.Customer.objects.all()
    return render(request, 'admin/view_customer.html', {'customers': customers})


# admin delete customer
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def delete_customer_view(request, pk):
    customer = models.Customer.objects.get(id=pk)
    user = models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def update_customer_view(request, pk):
    customer = models.Customer.objects.get(id=pk)
    user = models.User.objects.get(id=customer.user_id)

    if request.method == 'POST':
        user_form = forms.CustomerUserForm(request.POST, instance=user)
        customer_form = forms.CustomerForm(request.POST, request.FILES, instance=customer)

        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            customer_form.save()
            return redirect('view-customer')
    else:
        user_form = forms.CustomerUserForm(instance=user)
        customer_form = forms.CustomerForm(instance=customer)

    mydict = {'user_form': user_form, 'customer_form': customer_form}
    return render(request, 'admin/admin_update_customer.html', context=mydict)


# admin view the product
@login_required(login_url='admin_login')
@user_passes_test(is_admin_or_staff)
def admin_products_view(request):
    products = models.Product.objects.all()
    return render(request, 'admin/admin_products.html', {'products': products})


# admin add product by clicking on floating button
@login_required(login_url='admin_login')
@user_passes_test(is_admin_or_staff)
def admin_add_product_view(request):
    product_form = forms.ProductForm()
    if request.method == 'POST':
        product_form = forms.ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product_form.save()
        return HttpResponseRedirect('admin-products')
    return render(request, 'admin/admin_add_products.html', {'product_form': product_form})


@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def delete_product_view(request, pk):
    product = models.Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')


@login_required(login_url='admin_login')
@user_passes_test(is_admin_or_staff)
def update_product_view(request, pk):
    product = models.Product.objects.get(id=pk)
    product_form = forms.ProductForm(instance=product)
    if request.method == 'POST':
        product_form = forms.ProductForm(request.POST, request.FILES, instance=product)
        if product_form.is_valid():
            product_form.save()
            return redirect('admin-products')
    return render(request, 'admin/admin_update_product.html', {'product_form': product_form})


@login_required(login_url='admin_login')
@user_passes_test(is_admin_or_staff)
def admin_view_booking_view(request):
    ordered_items = get_ordered_items()
    return render(request, 'admin/admin_view_booking.html', {'data': ordered_items})


@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def delete_order_view(request, pk):
    order = models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')


# for changing status of order (pending,delivered...)
@login_required(login_url='admin_login')
@user_passes_test(is_admin_or_staff)
def update_order_view(request, pk):
    order = models.Orders.objects.get(id=pk)
    order_form = forms.OrderForm(instance=order)
    if request.method == 'POST':
        order_form = forms.OrderForm(request.POST, instance=order)
        if order_form.is_valid():
            order_form.save()
            return redirect('admin-view-booking')
    return render(request, 'admin/update_order.html', {'order_form': order_form})


# admin view the feedback
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def view_feedback_view(request):
    feedbacks = models.Feedback.objects.all().order_by('-id')
    return render(request, 'random/view_feedback.html', {'feedbacks': feedbacks})


def delete_feedback_view(request, feedback_id):
    try:
        feedback = models.Feedback.objects.get(pk=feedback_id)
        feedback.delete()
        return JsonResponse({'message': 'Feedback deleted successfully.'})
    except models.Feedback.DoesNotExist:
        return JsonResponse({'error': 'Feedback not found.'}, status=404)


# ----------------------------------------------------------------------------
# ------------------------ PUBLIC CUSTOMER RELATED VIEWS ---------------------
# ----------------------------------------------------------------------------

# Search bar, to search items on the main page
class SearchView(TemplateView):
    template_name = 'common/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        products = models.Product.objects.filter(name__icontains=query) if query else models.Product.objects.none()
        product_count_in_cart = get_product_count_in_cart(self.request)
        word = f"Searched Result : {query}" if query else ""
        context.update({'products': products, 'word': word, 'product_count_in_cart': product_count_in_cart})
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.template_name = 'customer/customer_home.html'
        return super().dispatch(request, *args, **kwargs)


# any one can add product to cart, no need of signin
def add_to_cart_view(request, pk):
    products = models.Product.objects.all()

    # for cart counter, fetching products ids added by customer from cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 1

    response = render(request, 'common/index.html',
                      {'products': products, 'product_count_in_cart': product_count_in_cart})

    # adding product id to cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids == "":
            product_ids = str(pk)
        else:
            product_ids = product_ids + "|" + str(pk)
        response.set_cookie('product_ids', product_ids)
    else:
        response.set_cookie('product_ids', pk)
    return response


# for checkout of cart
def cart_view(request):
    # for cart counter
    product_count_in_cart = get_product_count_in_cart(request)

    # fetching product details from db whose id is present in cookie
    products = None
    total = calculate_total_from_cookies(request)
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart = product_ids.split('|')
            products = models.Product.objects.filter(id__in=product_id_in_cart)
    return render(request, 'random/cart.html',
                  {'products': products, 'total': total, 'product_count_in_cart': product_count_in_cart})


def remove_from_cart_view(request, pk):
    # for counter in cart
    product_count_in_cart = get_product_count_in_cart(request)

    # removing product id from cookie
    total = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_id_in_cart = product_ids.split('|')
        product_id_in_cart = list(set(product_id_in_cart))
        product_id_in_cart.remove(str(pk))
        products = models.Product.objects.all().filter(id__in=product_id_in_cart)
        # for total price shown in cart after removing product
        for p in products:
            total = total + p.price

        #  for update cookie value after removing product id in cart
        value = ""
        for i in range(len(product_id_in_cart)):
            if i == 0:
                value = value + product_id_in_cart[0]
            else:
                value = value + "|" + product_id_in_cart[i]
        response = render(request, 'random/cart.html',
                          {'products': products, 'total': total, 'product_count_in_cart': product_count_in_cart})
        if value == "":
            response.delete_cookie('product_ids')
        response.set_cookie('product_ids', value)
        return response


# The customer can send a feedback to the admin(s)
class SendFeedbackView(FormView):
    template_name = 'random/send_feedback.html'
    form_class = forms.FeedbackForm
    success_url = 'feedback-sent'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_count_in_cart'] = get_product_count_in_cart(self.request)
        return context

    def get(self, request, *args, **kwargs):
        feedback_form = self.get_form()
        return render(request, self.template_name, {
            'feedback_form': feedback_form,
            'product_count_in_cart': get_product_count_in_cart(request),
        })

    def post(self, request, *args, **kwargs):
        feedback_form = self.get_form()
        if feedback_form.is_valid():
            return self.form_valid(feedback_form)
        else:
            return self.form_invalid(feedback_form)


def feedback_sent(request):
    product_count_in_cart = get_product_count_in_cart(request)
    return render(request, 'random/feedback_sent.html',
                  {'product_count_in_cart': product_count_in_cart})


# ------------------------------------------------------------------------------
# ------------------------ CUSTOMER RELATED VIEWS ------------------------------
# ------------------------------------------------------------------------------


@login_required(login_url='customer_login')
@user_passes_test(is_customer)
def customer_home_view(request):
    products = models.Product.objects.all()
    product_count_in_cart = get_product_count_in_cart(request)
    return render(request, 'customer/customer_home.html',
                  {'products': products, 'product_count_in_cart': product_count_in_cart})


# shipment address before placing order
# basically more cookies magic
@login_required(login_url='customer_login')
def customer_address_view(request):
    product_in_cart = False
    if 'product_ids' in request.COOKIES and request.COOKIES['product_ids']:
        product_in_cart = True

    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            email = address_form.cleaned_data['Email']
            mobile = address_form.cleaned_data['Mobile']
            address = address_form.cleaned_data['Address']
            response = redirect('payment_view')  # Redirect to the payment form
            response.set_cookie('email', email)
            response.set_cookie('mobile', mobile)
            response.set_cookie('address', address)
            return response
    else:
        address_form = AddressForm()

    product_count_in_cart = get_product_count_in_cart(request)
    return render(request, 'customer/customer_address.html',
                  {'addressForm': address_form, 'product_in_cart': product_in_cart,
                   'product_count_in_cart': product_count_in_cart})


def payment_view(request):
    email = None
    mobile = None
    address = None

    if 'email' in request.COOKIES:
        email = request.COOKIES['email']
    if 'mobile' in request.COOKIES:
        mobile = request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address = request.COOKIES['address']

    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            response = redirect('payment-success')
            return response
    else:
        payment_form = PaymentForm()
    total = calculate_total_from_cookies(request)
    product_count_in_cart = get_product_count_in_cart(request)
    return render(request, 'random/payment.html',
                  {'address': address, 'email': email, 'mobile': mobile, 'payment_form': payment_form, 'total': total,
                   'product_count_in_cart': product_count_in_cart})


@login_required(login_url='customer_login')
def payment_success_view(request):
    product_count_in_cart = get_product_count_in_cart(request)
    customer = models.Customer.objects.get(user_id=request.user.id)
    products = None
    email = None
    mobile = None
    address = None
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart = product_ids.split('|')
            products = models.Product.objects.all().filter(id__in=product_id_in_cart)

    if 'email' in request.COOKIES:
        email = request.COOKIES['email']
    if 'mobile' in request.COOKIES:
        mobile = request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address = request.COOKIES['address']

    for product in products:
        models.Orders.objects.get_or_create(customer=customer, product=product, status='Pending', email=email,
                                            mobile=mobile, address=address)

    response = render(request, 'random/payment_success.html', {'product_count_in_cart': product_count_in_cart})
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response


@login_required(login_url='customer_login')
@user_passes_test(is_customer)
def my_order_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    orders = models.Orders.objects.all().filter(customer_id=customer)
    product_count_in_cart = get_product_count_in_cart(request)
    ordered_products = []
    for order in orders:
        ordered_product = models.Product.objects.all().filter(id=order.product.id)
        ordered_products.append(ordered_product)

    return render(request, 'random/my_order.html',
                  {'data': zip(ordered_products, orders), 'product_count_in_cart': product_count_in_cart})


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return


@login_required(login_url='customer_login')
@user_passes_test(is_customer)
def download_invoice_view(request, orderID, productID):
    order = models.Orders.objects.get(id=orderID)
    product = models.Product.objects.get(id=productID)
    mydict = {
        'orderDate': order.order_date,
        'customerName': request.user,
        'customerEmail': order.email,
        'customerMobile': order.mobile,
        'shipmentAddress': order.address,
        'orderStatus': order.status,

        'productName': product.name,
        'productImage': product.product_image,
        'productPrice': product.price,
        'productDescription': product.description,

    }
    return render_to_pdf('random/download_invoice.html', mydict)


@login_required(login_url='customer_login')
@user_passes_test(is_customer)
def my_profile_view(request):
    product_count_in_cart = get_product_count_in_cart(request)
    customer = models.Customer.objects.get(user_id=request.user.id)
    return render(request, 'customer/my_profile.html',
                  {'customer': customer, 'product_count_in_cart': product_count_in_cart})


@login_required(login_url='customer_login')
@user_passes_test(is_customer)
def edit_profile_view(request):
    product_count_in_cart = get_product_count_in_cart(request)
    customer = models.Customer.objects.get(user_id=request.user.id)
    user = models.User.objects.get(id=customer.user_id)
    if request.method == 'POST':
        user_form = forms.CustomerUserForm(request.POST, instance=user)
        customer_form = forms.CustomerForm(request.POST, request.FILES, instance=customer)
        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            customer_form.save()
            customer.user = user
            login(request, user)
            return redirect('my-profile')
        else:
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            for field, errors in customer_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        user_form = forms.CustomerUserForm(instance=user)
        customer_form = forms.CustomerForm(instance=customer)

    mydict = {'user_form': user_form, 'customer_form': customer_form, 'product_count_in_cart': product_count_in_cart}
    return render(request, 'customer/edit_profile.html', context=mydict)


# -----------------------------------------------------------
# ------------------------ ABOUT US VIEW --------------------
# -----------------------------------------------------------


def about_us_view(request):
    products = models.Product.objects.all()
    product_count_in_cart = get_product_count_in_cart(request)

    return render(request, 'random/about_us.html',
                  {'products': products, 'product_count_in_cart': product_count_in_cart})


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)
