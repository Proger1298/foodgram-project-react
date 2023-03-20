from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(
        'Имя',
        max_length=150
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150
    )
    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
        max_length=254
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class BlackListedToken(models.Model):
    token = models.CharField(max_length=512)
    user = models.ForeignKey(
        User,
        related_name="token_user",
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заблокированный токен'
        verbose_name_plural = 'Заблокированные токены'
        unique_together = ("token", "user")


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подпсики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]
