from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

#https://stackoverflow.com/questions/37868084/how-do-i-add-an-option-in-django-model-choice-through-template
#https://stackoverflow.com/questions/33512105/how-to-access-to-tuple-values-in-a-if-statement-inside-a-forloop-in-django-templ
Categories = (
    ('a',"None"),
    ('b',"Clothes"),
    ('c',"Furniture"),
    ('d',"Electronics"),
    ('e',"Video Games"),
    ('f',"Home Appliances"),
    ('g',"Fashion"),
    ('h',"Sports")
)


class User(AbstractUser):
    pass

#https://stackoverflow.com/questions/53863318/django-operationalerror-no-such-column-on-pythonanywhere
#https://stackoverflow.com/questions/65420512/django-operationalerror-table-has-no-column-named-user-id


class bids(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name="userBid")
    price = models.FloatField()
    timeAdded = models.DateTimeField(default=timezone.now)


class Comments(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE , related_name="commentAuthor")
    text = models.CharField(max_length=200)
    timeAdded = models.DateTimeField(default=timezone.now)

class auctionListing(models.Model):
    title = models.CharField(max_length=64)
    desc = models.CharField(max_length=400)
    startingBid = models.FloatField()
    active = models.BooleanField(default=True)
    image = models.ImageField(null=True, blank = True, default='image.png')
    categoryType = models.CharField(max_length=1, default=Categories[0][1] , choices=Categories)
    listingOwner = models.ForeignKey(User, on_delete=models.CASCADE , related_name="listingOwner")
    usersWatching = models.ManyToManyField(User, blank=True, related_name="listingsWatched")
    comments = models.ManyToManyField(Comments, blank=True, related_name="comments")
    bids = models.ManyToManyField(bids, blank=True, related_name="bids")
    closed = models.BooleanField(default=False)
    buyer = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE ,related_name="buyer")
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE , related_name="winner")

