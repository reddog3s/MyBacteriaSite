from django.conf import settings
from django.db import models
from django_countries.fields import CountryField




from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver









class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    country = CountryField(null = True)
    birthdate = models.DateField(null = True)

    # class Meta:
    #      managed = False
    #      db_table = 'siteUser'

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()






class Microbe(models.Model):
    MicrobePhylum = models.CharField(max_length=100)
    MicrobeClass = models.CharField(max_length=100)
    MicrobeOrder = models.CharField(max_length=100)
    MicrobeFamily = models.CharField(max_length=100)
    MicrobeGenus = models.CharField(max_length=100)
    MicrobeSpecies = models.CharField(max_length=100)
    description = models.TextField()

    

    def __str__(self):
        return self.MicrobeSpecies



class MicrobePost(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    microbe = models.ForeignKey(Microbe, on_delete=models.SET_NULL, null = True, blank=True)
    created_date = models.DateTimeField(auto_now_add= True)
    last_edited= models.DateTimeField(auto_now= True)
    title = models.CharField(max_length=200)
    longitude = models.DecimalField(max_digits=6, decimal_places=3)
    latitude = models.DecimalField(max_digits=5, decimal_places=3)
    image = models.ImageField(blank = False)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='post_like')
    text = models.TextField(null = True, blank = True)

    def __str__(self):
        return self.title
    
    def number_of_likes(self):
        return self.likes.count()
    

    




