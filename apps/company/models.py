from django.db import models


class Company(models.Model):
    """ Модель компании """
    PROTECTOR_CHOICES = [
        ('all_season', 'Всесезонный'),
        ('summer', 'Лето'),
        ('winter', 'Зима'),
        ('winter_spikes', 'Зима/Шипы'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name='Company Name')
    description = models.TextField(null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    promotion = models.TextField(null=True, blank=True)
    protector = models.CharField(max_length=20, choices=PROTECTOR_CHOICES, null=True, blank=True)
    ad_order = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
