from django.db import models

# Create your models here.

class Request(models.Model):
    # implicit 'id' primary key field
    datetime = models.DateTimeField('date requested')
    repo = models.URLField(max_length=512)

    def __str__(self):
        return ", ".join([str(self.id), 
                          str(self.datetime), 
                          str(self.repo)])

class LogMessage(models.Model):
    # implicit 'id' primary key field
    request = models.ForeignKey(Request)
    datetime = models.DateTimeField('date published')
    payload = models.TextField('json payload')

    def __str__(self):
        return ", ".join([str(self.id), 
                          str(self.request), 
                          str(self.datetime), 
                          str(self.payload)])

