from django.test import TestCase
from .models import Thread, get_id, Post
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import reverse
from django.core.exceptions import ObjectDoesNotExist


class ModelsTests(TestCase):

    def get_test_thread(self, tid=0, thread_text='test',):
        # Метод возвращает объект Thread с текстом 'test' и заданным id
        if tid != 0:
            return Thread(id=tid, thread_text=thread_text)
        else:
            return Thread(thread_text=thread_text)

    # Проверка, что get_id возвращает строку из 7 символов
    def test_let_return_get_id(self):
        self.assertEqual(len(get_id(self.get_test_thread(tid=1))), 7)

    # Тесты проверяющие, что get_id возвращает корректное число при разных значениях id
    def test_get_id_with_1_id(self):
        self.assertEqual(get_id(self.get_test_thread(tid=1))[:4], '0001')

    def test_get_id_with_2_id(self):
        self.assertEqual(get_id(self.get_test_thread(tid=11))[:4], '0011')

    def test_get_id_with_3_id(self):
        self.assertEqual(get_id(self.get_test_thread(tid=111))[:4], '0111')

    def test_get_id_with_4_id(self):
        self.assertEqual(get_id(self.get_test_thread(tid=1111))[:4], '1111')

    # Тесты проверяют, создает ли метод create_thread экземпляр класса Thread,
    # есть ли у него 7-значный thread_id, создался ли невидимый пост.
    def test_thread_id_and_invisible_post(self):
        Thread.objects.create_thread(thread_text='test_thread_manager')
        test_thread = Thread.objects.get(thread_text='test_thread_manager')
        self.assertEqual(len(test_thread.thread_id), 7)
        self.assertEqual(test_thread.post_set.first().post_visible, False)

    # Тест проверяет, возвращает ли метод need_delete нужные значения
    def test_thread_need_delete(self):
        Thread.objects.create_thread(thread_text='test_need_delete')
        test_thread = Thread.objects.get(thread_text='test_need_delete')
        self.assertEqual(test_thread.need_delete(), False)
        post_posted_later = Post(post_thread=test_thread, post_text='test_need_delete_later',
                                 post_date=timezone.now() - timedelta(hours=7, ))
        post_posted_later.save()
        self.assertEqual(test_thread.need_delete(), False)
        post_posted_recently = Post(post_thread=test_thread, post_text='test_need_delete_recently',
                                    post_date=timezone.now() - timedelta(minutes=5))
        post_posted_recently.save()
        self.assertEqual(test_thread.need_delete(), False)
        self.assertEqual(test_thread.post_set.last(), post_posted_recently)

    # Тест проверяет создает ли метод create_post экземпляр класса Post
    # и есть ли у него 7-значный id
    def test_post_manager(self):
        Thread.objects.create_thread(thread_text='test_post_manager')
        thread_for_test_post_manager = Thread.objects.get(thread_text='test_post_manager')
        Post.objects.create_post(post_thread=thread_for_test_post_manager, post_text='test_post_manager')
        test_post = Post.objects.get(post_text='test_post_manager')
        self.assertEqual(len(test_post.post_id), 7)

    def test_thread_get_absolute_url(self):
        test_absolute_url = Thread.objects.create_thread(thread_text='test_absolute_url')
        self.assertEqual(test_absolute_url.get_absolute_url(), '/b/%s/' % test_absolute_url.pk)


class List_Thread_View_Test(TestCase):
    def test_responce_status_code(self):
        response = self.client.get(reverse('list_thread'))
        self.assertEqual(response.status_code, 200)

