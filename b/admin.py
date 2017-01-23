from django.contrib import admin
from .models import Post, Thread, Responses, Complaint
# Register your models here.

admin.site.register(Thread)
admin.site.register(Post)
admin.site.register(Responses)
admin.site.register(Complaint)