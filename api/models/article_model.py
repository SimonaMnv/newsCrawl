from django.db import models


class ArticleOfInterest(models.Model):
    title = models.CharField(max_length=255, unique=False)
    body = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
