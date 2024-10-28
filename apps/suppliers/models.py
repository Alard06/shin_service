from django.db import models


class Supplier(models.Model):
    """ Модель поставщика """
    name = models.CharField(max_length=100,
                            unique=True,
                            verbose_name='Name'
                            )
    article_number = models.CharField(max_length=100,
                                      unique=True,
                                      verbose_name='Article Number',
                                      blank=True,
                                      null=True
                                      )
    priority = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=[1])
    visual_priority = models.IntegerField(choices=[(1, 'Зеленый'), (2, 'Желтый'), (3, 'Красный')], default=[3])
    city = models.ForeignKey('City', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-priority', 'visual_priority']

    def __str__(self):
        return f"{self.name} - Priority {self.priority} - Visual: {self.visual_priority}"

class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


