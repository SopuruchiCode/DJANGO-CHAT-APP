from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime


def image_upload(instance, filename):
    username = instance.user.username
    name_of_file = filename.split(".")[0]
    ext = filename.split(".")[-1]
    origin_date = datetime.now().strftime("%Y_%m_%d--%H:%M:%S")
    return f"profile_pic/{username}/{name_of_file} {origin_date}.{ext}"


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=254)

    def __str__(self):
        return f"{self.username}"


class Account(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True)
    user_string = models.CharField(max_length=100, default="None")
    profile_picture = models.ImageField(upload_to=image_upload, default="defaults/profile_pic/default-profile-pic.png")
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if (self.user_string == "None") and (self.user != None):
            self.user_string = self.user.username
        return super(Account, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_string}"


########## EXPERIMENTAL ########## 

# class FriendList(models.Model):
#     owner = models.OneToOneField(Account)
#     accounts = models.ManyToManyField(Account)
    
# class FriendshipAge(models.Model):
#     date_created = models.DateTimeField(auto_now_add=True)
#     friends = models.JSONField(default=list)

# class FriendRequest(models.Model):
#     initiator = models.ForeignKey(Account, on_delete=models.CASCADE)
#     recipient = models.ForeignKey(Account, on_delete=models.CASCADE)
#     accepted = models.BooleanField(default=False)

########## EXPERIMENTAL ##########