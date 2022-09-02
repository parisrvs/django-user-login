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

### 04.	Run `python manage.py migrate` to create the `User`, `Person` and `Address` models (you'll need the Admin app enabled).

### 05.	The App requires [Django Sessions](https://docs.djangoproject.com/en/4.0/topics/http/sessions/#enabling-sessions)

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
- #### To Login, use anyone one of these

                - <a href="{% url 'authentication:homepage' %}">Login</a>
                - <a href='/authentication/'>Login</a>

- #### To Logout, use anyone one of these

                - <a href="{% url 'authentication:logout' %}">Logout</a>
                - <a href="/authentication/logout/">Logout</a>

- #### To visit My Account page and edit profile credentials, use any one of these -

                - <a href="{% url 'authentication:account' %}">Account</a>
                - <a href="/authentication/account/">Account</a>

### 08. When `AUTHENTICATION_DEBUG = TRUE`

        - Live EMAILS will not be sent and verification codes, if any, will be displayed in the console.
        - No password validation will happen.

### 09. This authentication app creates two models - `Person` and `Address`

        class Person(models.Model):
        MALE = 'M'
        FEMALE = 'F'
        NON_BINARY = 'N'
        GENDER_CHOICES = [
                (MALE, "male"),
                (FEMALE, 'female'),
                (NON_BINARY, 'non_binary')
        ]

        user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="person")
        first_name = models.CharField(max_length=64, blank=True, null=True)
        last_name = models.CharField(max_length=64, blank=True, null=True)
        email = models.EmailField(unique=True, blank=True, null=True)
        username = models.CharField(max_length=64, blank=True, null=True)
        gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
        phone = models.CharField(max_length=20, unique=True, blank=True, null=True)
        birth_date = models.DateField(null=True, blank=True)

        class Meta:
                ordering = ['first_name', 'last_name']

        def __str__(self):
                return f"{self.first_name} {self.last_name}"


        class Address(models.Model):
        person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="address")
        primary = models.BooleanField(default=False)
        first_name = models.CharField(max_length=200)
        last_name = models.CharField(max_length=200)
        email = models.EmailField(max_length=500)
        mobile = models.CharField(max_length=20)
        homephone = models.CharField(max_length=20, null=True, blank=True)
        address1 = models.CharField(max_length=2000)
        address2 = models.CharField(max_length=2000, null=True, blank=True)
        landmark = models.CharField(max_length=500)
        pincode = models.CharField(max_length=10)
        city = models.CharField(max_length=50)
        state = models.CharField(max_length=50)
        country = models.CharField(max_length=50)

        def __str__(self):
                return f"{self.first_name} {self.last_name}"
        
        class Meta:
                ordering = ['first_name', 'last_name']
                verbose_name_plural = "Address Entries"

### 10. When a user closes their account, the app will not delete the User account but set `is_active` to `False` in [User Model](https://docs.djangoproject.com/en/4.1/ref/contrib/auth/#django.contrib.auth.models.User.is_active)

### 11. Check [Demo Website](https://django-user-login.herokuapp.com/)