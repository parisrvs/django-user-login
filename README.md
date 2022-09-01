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

### 03.	The App requires [Django Sessions](https://docs.djangoproject.com/en/4.0/topics/http/sessions/#enabling-sessions)

### 04.	Include the authentication URLconf in your project urls.py like this:

		path('authentication/', include('authentication.urls')),

### 05.	Run `python manage.py makemigrations && python manage.py migrate` to create the User models (you'll need the Admin app enabled).

### 06.  In your settings.py file include the following:

        SITE_TITLE = 'your-site-title'
        LOGIN_URL = '/authentication/'
        EMAIL_HOST = 'email-host'
        EMAIL_PORT = email-port
        EMAIL_HOST_USER = 'emaill-address'
        EMAIL_HOST_PASSWORD = 'email-password
        EMAIL_USE_TLS = True
        AUTHENTICATION_DEBUG=False

### 07.  For login and logout functionality, use - 
- #### To Login, use anyone of these

            - <a href="{% url 'authentication:homepage' %}">Login</a>
		    - <a href='/authentication/'>Login</a>

- #### To Logout, use anyone of these

            - <a href="{% url 'authentication:logout' %}">Logout</a>
		    - <a href="/authentication/logout/">Logout</a>

- #### To visit My Account page and edit profile credentials, use any one of these -

            - <a href="{% url 'authentication:account' %}">Account</a>
            - <a href="/authentication/account/">Account</a>

### 08. When AUTHENTICATION_DEBUG = TRUE

            - Live EMAILS will not be sent and verification codes, if any, will be printed on the 
            console
            - No password validation will happen.

### 08. Check [Demo Website](https://django-user-login.herokuapp.com/)



