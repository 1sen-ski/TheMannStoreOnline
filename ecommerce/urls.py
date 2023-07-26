from django.contrib import admin
from django.urls import path
from ecommerce.ecom import views
from ecommerce.ecom.views import CustomLoginView, Custom_Admin_LoginView, CustomLogoutView, IndexView, SearchView, \
    SendFeedbackView

handler404 = 'ecommerce.ecom.views.custom_404_view'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='home'),
    path('after_login', views.after_login_view, name='after_login'),
    path('logout', CustomLogoutView.as_view(), name='logout'),
    path('about_us', views.about_us_view, name='about_us'),
    path('search/', SearchView.as_view(), name='search'),
    path('send-feedback', SendFeedbackView.as_view(), name='send-feedback'),
    path('view-feedback', views.view_feedback_view, name='view-feedback'),
    path('feedback-sent', views.feedback_sent, name='feedback_sent'),
    path('delete-feedback/<int:feedback_id>/', views.delete_feedback_view, name='delete_feedback'),

    path('admin_click', views.admin_click_view),
    path('admin_login', Custom_Admin_LoginView.as_view(), name='admin_login'),
    path('admin-dashboard', views.admin_dashboard_view, name='admin-dashboard'),

    path('view-customer', views.view_customer_view, name='view-customer'),
    path('delete-customer/<int:pk>', views.delete_customer_view, name='delete-customer'),
    path('update-customer/<int:pk>', views.update_customer_view, name='update-customer'),

    path('admin-products', views.admin_products_view, name='admin-products'),
    path('admin-add-product', views.admin_add_product_view, name='admin-add-product'),
    path('delete-product/<int:pk>', views.delete_product_view, name='delete-product'),
    path('update-product/<int:pk>', views.update_product_view, name='update-product'),

    path('admin-view-booking', views.admin_view_booking_view, name='admin-view-booking'),
    path('delete-order/<int:pk>', views.delete_order_view, name='delete-order'),
    path('update-order/<int:pk>', views.update_order_view, name='update-order'),

    path('customer_signup', views.customer_signup_view),
    path('customer_login', CustomLoginView.as_view(), name='customer_login'),
    path('customer-home', views.customer_home_view, name='customer-home'),
    path('my-order', views.my_order_view, name='my-order'),
    path('my-profile', views.my_profile_view, name='my-profile'),
    path('edit-profile', views.edit_profile_view, name='edit-profile'),
    path('download-invoice/<int:orderID>/<int:productID>', views.download_invoice_view, name='download-invoice'),

    path('add-to-cart/<int:pk>', views.add_to_cart_view, name='add-to-cart'),
    path('cart', views.cart_view, name='cart'),
    path('remove-from-cart/<int:pk>', views.remove_from_cart_view, name='remove-from-cart'),
    path('customer-address', views.customer_address_view, name='customer-address'),
    path('payment-success', views.payment_success_view, name='payment-success'),
    path('payment', views.payment_view, name='payment_view')
]
