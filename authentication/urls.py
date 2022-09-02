from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('logout/', views.logout_view, name='logout'),

    path('register/', views.register),
    path('register/verify/', views.verifyregistration),
    path('register/verify/resend/', views.verifyRegistrationCodeResend),
    path('register/verify/cancel/', views.cancelregistration),

    path('recover/', views.recover),
    path('recover/verify/', views.verifyrecovery),
    path('recover/verify/cancel/', views.cancelrecovery),
    path('recover/verify/resend/', views.verifyRecoverCodeResend),
    path('recover/verify/changepassword/', views.verifyChangePassword),

    path('account/', views.account, name='account'),
    path('account/close/', views.closeAccount),
    path('account/editUser/', views.editUser),
    path('account/getUser/', views.getUser),
    path('account/addAddress/', views.addAddress),
    path('account/getAddress/', views.getAddress),
    path('account/editAddress/', views.editAddress),
    path('account/deleteAddress/', views.deleteAddress),
    path('account/makeAddressPrimary/', views.makeAddressPrimary),

    path('account/editEmail/', views.editEmail),
    path('account/editEmail/cancel/', views.cancelEmailChange),
    path('account/editEmail/ResendCode/', views.editEmailResendCode),
    path('account/editEmail/verify/', views.editEmailVerify),
    path('account/updatepassword/', views.updatepassword),

]