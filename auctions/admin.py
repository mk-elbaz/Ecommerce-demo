from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(User)
admin.site.register(auctionListing)
admin.site.register(bids)
admin.site.register(Comments)

