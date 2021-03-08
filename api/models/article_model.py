from djongo import models
from django_elasticsearch_dsl_drf.wrappers import dict_to_obj


class ArticleOfInterest(models.Model):
    _id = models.ObjectIdField()
    title = models.TextField(null=False, blank=False)
    date = models.DateTimeField(null=False, blank=False)
    body = models.TextField(null=False, blank=False)
    tags = models.TextField(null=True, blank=True)
    author = models.CharField(max_length=255, unique=False)
    link = models.TextField(null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    scope = models.TextField(null=True, blank=True)

    acts_committed = models.TextField(null=True, unique=False, blank=True)
    location_of_crime = models.CharField(max_length=255, null=True, unique=False)
    ages_of_involved = models.CharField(max_length=255, null=True, unique=False)
    time_of_crime = models.CharField(max_length=255, null=True, unique=False)
    victim_gender = models.CharField(max_length=255, null=True, unique=False)
    criminal_status = models.CharField(max_length=255, null=True, unique=False)
    drug_type = models.CharField(max_length=255, null=True, unique=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'db_crime_article'

    @property
    def article_analysis(self):
        wrapper = dict_to_obj({
            'acts_committed': self.acts_committed,
            'location_of_crime': self.location_of_crime,
            'ages_involved': self.ages_of_involved,
            'time_of_crime': self.time_of_crime,
            'victim_gender': self.victim_gender,
            'criminal_status': self.criminal_status,
            'drug_type': self.drug_type

        })

        return wrapper

# python manage.py makemigrations api  -> track changes
# python manage.py sqlmigrate api XXXX
# python manage.py migrate

# if db is deleted -> python manage.py createsuperuser
