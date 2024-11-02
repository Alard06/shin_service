from django.db import models

class Company(models.Model):
    """ Модель компании """
    name = models.CharField(max_length=100, unique=True, verbose_name='Company Name')

    def __str__(self):
        return self.name
