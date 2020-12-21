from djongo import models


class PersonOfInterest(models.Model):
    type = models.CharField(max_length=255, null=True, unique=False)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, unique=False)
    ethnicity = models.CharField(max_length=255, null=True, unique=False)

    def __str__(self):
        return self.type

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

# python manage.py makemigrations api  -> track changes
# python manage.py sqlmigrate api XXXX
# python manage.py migrate

# if db is deleted -> python manage.py createsuperuser

