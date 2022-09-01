from django.db import models
from django.contrib.auth.models import User


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