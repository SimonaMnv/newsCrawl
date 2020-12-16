from django.db import models


class PersonOfInterest(models.Model):
    name = models.CharField(max_length=4096, null=True, unique=False)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=4096, null=True, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'db_person'


class Criminal(PersonOfInterest):
    def __init__(self, *args, **kwargs):
        super(PersonOfInterest, self).__init__(*args, **kwargs)
        self.type = "criminal"

    class Meta:
        db_table = 'db_criminal'


class Victim(PersonOfInterest):
    def __init__(self, *args, **kwargs):
        super(PersonOfInterest, self).__init__(*args, **kwargs)
        self.type = "victim"

    class Meta:
        db_table = 'db_victim'

# python manage.py makemigrations API  -> track changes
# python manage.py sqlmigrate API XXXX
# python manage.py migrate

# if db is deleted -> python manage.py createsuperuser
