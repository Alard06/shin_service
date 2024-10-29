from django.db import models

from apps.company.models import Company

class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    """ Модель поставщика """
    name = models.CharField(max_length=100, unique=True, verbose_name='Name')
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class CompanySupplier(models.Model):
    """ Модель для хранения индивидуального артикула поставщика для каждой компании """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    article_number = models.CharField(max_length=100, verbose_name='Article Number', blank=True, null=True)
    priority = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=1, null=True, blank=True)
    visual_priority = models.IntegerField(choices=[(1, 'Зеленый'), (2, 'Желтый'), (3, 'Красный')], default=3, null=True, blank=True)

    class Meta:
        unique_together = ('company', 'supplier')

    def __str__(self):
        return f"{self.company.name} - {self.supplier.name} - Article: {self.article_number} - Priority: {self.priority} - Visual: {self.visual_priority}"