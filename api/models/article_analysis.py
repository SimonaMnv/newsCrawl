from djongo import models


class CrimeAnalysis(models.Model):
    location_of_crime = models.CharField(max_length=255, null=True, unique=False)
    ages_involved = models.IntegerField(null=True, blank=True)
    time_of_crime = models.CharField(max_length=255, null=True, unique=False)
    victim_gender = models.CharField(max_length=255, null=True, unique=False)

    def __str__(self):
        return self.location_of_crime

    class Meta:
        db_table = 'db_analysis'

# python manage.py makemigrations api  -> track changes
# python manage.py sqlmigrate api XXXX
# python manage.py migrate

# if db is deleted -> python manage.py createsuperuser
