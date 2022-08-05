from django.db import models
from accounts.models import User
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=255, )
    description = models.TextField()
    image = models.ImageField(
        upload_to="uploads/%Y/%m/%d/", default = None)
    project_url = models.URLField(max_length = 200, blank=True)
    votes = models.ManyToManyField(
        User, related_name='vote', default=None, blank=True)
    vote_count = models.BigIntegerField(default='0')
    hunter = models.ForeignKey(User, on_delete=models.CASCADE)
    users_collection = models.ManyToManyField(
        User, related_name='users_collection', default=None, blank=True)

    publish = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def get_absolute_url(self):
        return reverse('detail', args=[self.pk])

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-publish']
    class MPTTMeta:
        order_insertion_by = ['publish']

    




    
class Comment(MPTTModel):
    author = models.ForeignKey(User, related_name='author',
                               on_delete=models.CASCADE, default=None, blank=True)
    product = models.ForeignKey(Product,
                             on_delete=models.CASCADE,
                             related_name='comments')
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='children')
    content = models.TextField()
    publish = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ['publish']


class Offer(models.Model):
    user = models.ForeignKey(User, related_name='user',
                               on_delete=models.CASCADE, default=None, blank=True)
    product = models.ForeignKey(Product,
                             on_delete=models.CASCADE,
                             related_name='offers')
    sender_email = models.EmailField(default=True)
    message = models.TextField()
    publish = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-publish']