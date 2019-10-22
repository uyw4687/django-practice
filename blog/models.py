from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    title = models.CharField(max_length=64)
    content = models.TextField()
    author = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='article_set',
    )
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    article = models.ForeignKey(
            Article,
            on_delete=models.CASCADE,
            related_name='comment_set',
    )
    content = models.TextField()
    author = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='comment_set',
    )

    def __str__(self):
        return self.content
