from django.db import models

class User(models.Model):
    created = models.DateTimeField(auto_now_add=True)
