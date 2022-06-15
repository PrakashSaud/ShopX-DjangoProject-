from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .forms import LoginForm, MyPasswordChangeForm, MyPasswordResetForm, MySetPasswordForm


urlpatterns = [
    path('', views.ProductView.as_view(), name="home"),
    path('product-detail/<int:pk>', views.ProductDetailView.as_view(), name='product-detail'),

    # urls related to different products
    path('wines/', views.wine, name='wines'),
    path('wines/<slug:data>', views.wine, name='winedata'),
    path('gins/', views.gin, name='gins'),
    path('gins/<slug:data>', views.gin, name='gindata'),
    path('rums/', views.rum, name="rums"),
    path('rums/<slug:data>', views.rum, name="rumdata"),
    path('tequilas/', views.tequila, name="tequilas"),
    path('tequilas/<slug:data>', views.tequila, name="tequiladata"),
    path('whiskeys/', views.whiskey, name="whiskeys"),
    path('whiskeys/<slug:data>', views.whiskey, name="whiskeydata"),
    
    #urls related to accounts authentication
    path('registration/', views.CustomerRegistrationView.as_view(), name='customerregistration'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='app/login.html', authentication_form=LoginForm), name="login"),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    #password change urls
    path('changepassword/', auth_views.PasswordChangeView.as_view(template_name='app/passwordchange.html', form_class=MyPasswordChangeForm, success_url='/passwordchangedone/'), name='changepassword'),
    path('passwordchangedone/', auth_views.PasswordChangeDoneView.as_view(template_name='app/passwordchangedone.html'), name='passwordchangedone'),

    # password reset urls
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='app/password_reset.html', form_class=MyPasswordResetForm), name='password_reset'),
    path('password-reset/done', auth_views.PasswordResetDoneView.as_view(template_name='app/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='app/password_reset_confirm.html', form_class=MySetPasswordForm), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='app/password_reset_complete.html'), name="password_reset_complete"),

    #Profile urls
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('address/', views.address, name='address'),

    #Cart urls
    path('add-to-cart/', views.add_to_cart, name="add_to_cart"),
    path('cart/', views.show_cart, name='showcart'),
    path('pluscart/', views.plus_cart),
    path('minuscart/', views.minus_cart),
    path('removecart/', views.remove_cart),

    #
    path('checkout/', views.checkout, name='checkout'),
    path('paymentdone/', views.payment_done, name="paymentdone"),
    
    path('buy/', views.buy_now, name='buy-now'),
    path('orders/', views.orders, name='orders'),
    
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
