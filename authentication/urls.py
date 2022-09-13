from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('register/', views.register),
    path('register/verify/', views.verifyregistration),
    path('register/verify/resend-code/', views.verifyRegistrationCodeResend),
    path('register/verify/cancel/', views.cancelregistration),

    path('recover/', views.recover),
    path('recover/verify/', views.verifyrecovery),
    path('recover/verify/cancel/', views.cancelrecovery),
    path('recover/verify/resend-code/', views.verifyRecoverCodeResend),
    path('recover/verify/change-password/', views.verifyChangePassword),

    path('account/', views.account, name='account'),
    path('account/close/', views.closeAccount),
    path('account/close/cancel/', views.cancelAccountClosure),
    path('account/close/verify/', views.accountClosure),
    path('account/close/verify/resend-code/', views.resendCloseAccountVerificationCode),
    path('account/change-password/', views.changepassword),
    path('account/get-user/', views.getUser),
    path('account/edit-details/', views.editDetails),
    path('account/edit-email/', views.editEmail),
    path('account/edit-email/verify/', views.edit_email),
    path('account/edit-email/cancel/', views.editEmailCancel),
    path('account/edit-email/verify/resend-code/', views.resentEditEmailVerificationCode)
]
