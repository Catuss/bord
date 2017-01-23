from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import reverse


def get_id(qs_object):
    """
    Метод возвращает айди основаный на колличестве постов
    Треды не считаются, но у каждого треда есть скрытый пост для правильной сортировки
    из-за этого цифра получается верной.

    Скорее всего будут траблы в случае одновременного создания нескольких постов
    потестить, по необходимости - переделать. 
    """
    id = Post.objects.count()
    take_id = '0' * (5 - len(str(id))) + str(id)
    return take_id


class ThreadManager(models.Manager):
    def create_thread(self, thread_text, thread_media, sid):
        """
        Функция служит оберткой для стандартного метода create
        При создании нового треда в нем сразу создается один невидимый пост
        Это делается для обеспечения правильной сортировки

        sid: session id 

        Принимает 3 параметра: текст, изображение и ключ ОП'a будущего поста.

        Так же добавляет айди, в виде строки из цифр.
        """
        thread = self.create(thread_text=thread_text, thread_media=thread_media)
        thread.post_set.create(post_text='Не смотри не меня.', post_visible=False)
        thread.thread_id = get_id(thread)
        thread.thread_op = sid
        thread.save()
        return thread


class PostManager(models.Manager):
    def create_post(self, post_thread, post_text,
                    post_media, responses, sage, op):
        """
        Обертка для стандартного метода create

        Аргументы:

        post_text: текст поста
        post_media: изображение поста
        responses: ответы на другие посты
        sage: 'сажа'
        op: 'галка ОП'a

        Добавляет к нему айди и возвращает экземляр модели Post.
        """
        last_post = post_thread.post_set.last()             # Костылемагия сортировки
        last_post.post_latest = False                       # Сортировка идет только по последнему посту
        last_post.save()
        post = self.create(post_thread=post_thread, post_text=post_text,
                           post_media=post_media, post_sage=sage)
        post.post_id = get_id(post)

        # Если пост написан автором треда - добавляет булевое значение в бд 
        if op:
            post.post_write_op = True

        # Если пост с "сажей", то поле даты, по которому сортируются посты 
        # Приравнивается к дате прошлого поста.
        # (Если оставить это значение пустым - после такого поста тред станет последним)     
        if sage:
            post.post_sys_date = last_post.post_sys_date

        # Если пост содержит ответы на другие посты
        # В цикле проверяется, это ответ на тред, или на пост и у него в поле ответов создается новая запись
        # Тоже довольно кривая реализация, по возможности переделать.    
        if responses:
            for i in responses:
                try:
                    cur_thread = Thread.objects.get(thread_id=i)
                    cur_thread.responses_set.create(response=post.post_id)
                except:
                    pass
                try:
                    cur_post = Post.objects.get(post_id=i)
                    cur_post.responses_set.create(response=post.post_id)
                except:
                    pass
        post.save()
        return post


class Thread(models.Model):
    class Meta:
        verbose_name = "тред"
        verbose_name_plural = 'треды'

    objects = ThreadManager()
    thread_id = models.CharField(blank=True, null=True, max_length=7, unique=True)
    thread_date = models.DateTimeField(auto_now_add=True)
    thread_text = models.TextField(max_length=2048)
    thread_media = models.ImageField(upload_to='b/%m', blank=False, null=False)
    thread_op = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.thread_text[:20]

    def need_delete(self):
        """
        Если последний пост в треде был опубликован более 5 часов назад - возвращает True

        Как возникнет необходимость, добавить дополнительные проверки
        например, что в треде >= 500 постов

        С помощью этого сделать автосмыв
        """
        if self.post_set.last().post_date + timedelta(hours=5) <= timezone.now():
            return True
        else:
            return False

    def delete(self, *args, **kwargs):
        self.media.delete(save=False)
        super(Thread, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('detail_thread', kwargs={'pk': self.pk})


class Post(models.Model):
    class Meta:
        ordering = ('post_date',)
        verbose_name = "пост"
        verbose_name_plural = 'посты'

    def __str__(self):
        return self.post_text[:20]

    objects = PostManager()
    post_thread = models.ForeignKey(Thread)
    post_id = models.CharField(blank=True, null=True,  max_length=7, unique=True)
    post_date = models.DateTimeField(auto_now_add=True)
    post_sys_date = models.DateTimeField(auto_now_add=True, db_index=True,
                                         null=True, blank=True)
    post_text = models.TextField(max_length=2048)
    post_media = models.ImageField(blank=True, null=True, upload_to='b/%m')
    post_visible = models.BooleanField(default=True)
    post_latest = models.BooleanField(default=True)
    post_write_op = models.BooleanField(default=False)
    post_sage = models.BooleanField(default=False)


class Responses(models.Model):
    def __str__(self):
        return self.response
    response = models.CharField(max_length=7)
    post = models.ForeignKey(Post, blank=True, null=True)
    thread = models.ForeignKey(Thread, blank=True, null=True)


class Complaint(models.Model):
    def __str__(self):
        return self.text

    @classmethod
    def create(self, text, target):
        """ 
        Такой же алгоритм, как и в пост менеджере с ответами
        По возможности - переделать.
        """
        post, thread = None, None
        try:
            post = Post.objects.get(post_id=target)
        except:
            pass
        try:    
            thread = Thread.objects.get(thread_id=target)
        except:
            pass
        if post:
            new_comp = self.objects.create(text=text, post=post)
        elif thread:
            new_comp = self.objects.create(text=text, thread=thread)
        return

    text = models.CharField(max_length=500)
    post = models.ForeignKey(Post, blank=True, null=True)
    thread = models.ForeignKey(Thread, blank=True, null=True)
