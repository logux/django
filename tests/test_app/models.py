from django.contrib.auth.models import AbstractUser
from django.db import models


class Cat(models.Model):
    name = models.CharField(verbose_name='name', max_length=64)
    age = models.IntegerField(verbose_name='age')

    class Meta:
        verbose_name = 'cat'
        verbose_name_plural = 'cats'

    def __str__(self):
        return f'Cat {self.name} {self.age} years old'


class User(AbstractUser):
    first_name_meta = models.TextField(default='{}')

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
