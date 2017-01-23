from django.forms import Form, CharField, ImageField, Textarea, BooleanField


class Create_Thread_Form(Form):
    thread_text = CharField(label='Текст', max_length=1024, widget=Textarea)
    thread_media = ImageField(label='Пикча')


class Post_Form(Form):
    post_text = CharField(label='Текст', max_length=1024, widget=Textarea)
    post_media = ImageField(label='Пикча', required=False)
    post_res = CharField(max_length=480, label='hidden',
                         widget=Textarea, required=False)
    sage = BooleanField(required=False)
    op = BooleanField(required=False)


class Complaint_Form(Form):
    complaint_text = CharField(label="Что с этим постом не так?",
                               max_length=1024, widget=Textarea)
    complaint_target = CharField(label='hidden')
