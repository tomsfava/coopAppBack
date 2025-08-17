from django.db import models


class Macroregion(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Macroregião'
        verbose_name_plural = 'Macroregiões'


class Region(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)
    macroregion = models.ForeignKey(
        Macroregion, on_delete=models.SET_NULL, null=True, related_name='regions'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Região'
        verbose_name_plural = 'Regiões'


class MacroregionAffinity(models.Model):
    name = models.CharField(max_length=5, unique=True, blank=True)
    macroregion1 = models.ForeignKey(
        Macroregion, on_delete=models.CASCADE, related_name='affinities_as_source'
    )
    macroregion2 = models.ForeignKey(
        Macroregion, on_delete=models.CASCADE, related_name='affinities_as_target'
    )
    value = models.IntegerField('Valor de afinidade', null=False)

    class Meta:
        verbose_name = 'Afinidade de Macroregiões'
        verbose_name_plural = 'Afinidades de Macroregiões'
        unique_together = ('macroregion1', 'macroregion2')

    def save(self, *args, **kwargs):
        if self.macroregion1 == self.macroregion2:
            self.value = 1

        if self.macroregion1_id > self.macroregion2_id:
            self.macroregion1, self.macroregion2 = self.macroregion2, self.macroregion1

        name1 = self.macroregion1.name[:2].upper()
        name2 = self.macroregion2.name[:2].upper()
        self.name = f'{name1}-{name2}'

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} -{self.value}'
