from django.db import models


class ArticleOfInterest(models.Model):
    title = models.TextField(null=False, blank=False)
    date = models.DateTimeField(null=False, blank=False)
    body = models.TextField(null=False, blank=False)
    tags = models.TextField(null=True, blank=True)
    author = models.CharField(max_length=255, unique=False)
    link = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'db_article'
