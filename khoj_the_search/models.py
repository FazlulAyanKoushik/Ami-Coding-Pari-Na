from django.db import models
from account.models import User

# Create your models here.
class KhojTheSearch(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    int_list = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.int_list