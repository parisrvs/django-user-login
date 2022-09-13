# Authentication
A django user authentication and login application.

### 01.  To install and use the package, use:
        
        pip install django-user-login

Instructions

### 02.	Add "authentication" to your INSTALLED_APPS setting like this:

        INSTALLED_APPS = [
            ...
            'authentication',
        ]

### 03.	Include the authentication URLconf in your project urls.py like this:

	path('authentication/', include('authentication.urls')),

### 04.	Run `python manage.py migrate` to create the `User` model (you'll need the Admin app enabled).

### 05.	The App requires [Django Sessions](https://docs.djangoproject.com/en/4.0/topics/http/sessions/#enabling-sessions)

### 06.  In your settings.py file include the following:

        SITE_TITLE = 'site-title' # title of your site
        LOGIN_URL = '/authentication/'
        EMAIL_HOST = 'email-host' # e.g. 'smtp-mail.outlook.com'
        EMAIL_PORT = email-port # e.g. 587
        EMAIL_HOST_USER = 'email-address'
        EMAIL_HOST_PASSWORD = 'email password'
        EMAIL_USE_TLS = True
        AUTHENTICATION_DEBUG = Boolean # True or False (use False in production)
        VERIFICATION_CODE_VALIDITY_IN_MINUTES = Integer # int in the range of [1, 60] only

### 07.  For login and logout functionality, use - 
- #### To Login, use anyone one of these

                - <a href="{% url 'authentication:login' %}">Login</a>
                - <a href='/authentication/'>Login</a>

- #### To Logout, use anyone one of these

                - <a href="{% url 'authentication:logout' %}">Logout</a>
                - <a href="/authentication/logout/">Logout</a>

- #### To visit My Account page and edit profile credentials, use any one of these -

                - <a href="{% url 'authentication:account' %}">Account</a>
                - <a href="/authentication/account/">Account</a>

### 08. When `AUTHENTICATION_DEBUG = TRUE`

        - Live EMAILS will not be sent and verification codes / messages, if any, will be displayed in the terminal.
        - No password validation will happen.

### 09. When a user closes their account, the app will not delete the `User` but set `is_active` to `False` (see: [User Model](https://docs.djangoproject.com/en/4.1/ref/contrib/auth/#django.contrib.auth.models.User.is_active)) and `set_unusable_password()` (see: [Methods](https://docs.djangoproject.com/en/4.1/ref/contrib/auth/#django.contrib.auth.models.User.set_unusable_password)).

### 10. Check [Demo Website](https://django-user-login.herokuapp.com/)