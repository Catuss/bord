from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.http import HttpResponse
from .models import Post, Thread, Complaint
from .forms import Create_Thread_Form, Post_Form, Complaint_Form
from django.shortcuts import redirect, render_to_response, render, reverse
from b.OP import sid, set_sid


class Thread_List_View(ListView):
    page_kwarg = "page"
    context_object_name = 'thread'
    paginate_by = 10
    template_name = 'b_list.html'
    form = None

    def get(self, request, *args, **kwargs):
        self.form = Create_Thread_Form()
        self.path = request.path
        return super(Thread_List_View, self).get(request, *args, **kwargs)
    
    def get_queryset(self):
        """ 
        Параметры фильтрации и сортировки для вывода тредов в нужном порядке
        Не знаю, насколько это удачная реализация - тесты покажут. 
        """ 
        queryset = Thread.objects.order_by('-post__post_sys_date').filter(post__post_latest=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Thread_List_View, self).get_context_data(**kwargs)
        context['form'] = self.form
        context['three_two_one'] = [3, 2, 1]
        context['path'] = self.path
        return context

    def post(self, request, *args, **kwargs):
        form = Create_Thread_Form(request.POST, request.FILES)
        self.path = request.path
        if form.is_valid():
            thread_text = form.cleaned_data['thread_text']
            thread_media = form.cleaned_data['thread_media']
            thread_sid = set_sid(request)
            new_thread = Thread.objects.create_thread(thread_text, thread_media, thread_sid)
            return redirect(new_thread.get_absolute_url())
        else:
            return redirect(reverse('list_thread'))

class Thread_Detail_view(DetailView):
    model = Thread
    template_name = 'b_detail.html'
    context_object_name = 'thread'

    def get(self, request, *args, **kwargs):
        self.path = request.path
        return super(Thread_Detail_view, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Thread_Detail_view, self).get_context_data(**kwargs)
        context['path'] = self.path
        return context


class Update_List_Post_View(DetailView):
    """ 
    Класс отдающий список постов по конкретному треду
    К нему летят ajax запросы для обновления треда
    """
    model = Thread
    template_name = 'includes/b_update_list.html'


def complaint_view(request):
    """
    Метод обрабатывает ajax запросы поступающие с формы жалоб
    Хз, что произойдет если будет передана не валидная форма
    Не забыть потестить.
    """
    if request.method == 'POST':
        comp_text = request.POST.get('complaint_text', '')
        comp_target = request.POST.get('complaint_target', '')
        form = Complaint_Form({'complaint_text': comp_text,
                               'complaint_target': comp_target})
        if form.is_valid():
            Complaint.create(text=form.cleaned_data['complaint_text'],
                             target=form.cleaned_data['complaint_target'])
            return HttpResponse('ok', content_type='text/html')
        else:
            return HttpResponse('Текст ввести не забыл?', content_type='text/html')
    form = Complaint_Form()
    return render(request, 'includes/b_complaint.html', {'form': form})


def posting_view(request, pk):
    """ 
    Метод для постинга со страницы списка тредов
    К нему обращается ajax форма

    По сути, дублирует много кода из деталки
    по возможности - переделать.
    """
    if request.method == 'POST':
        if 'poster' in request.COOKIES:
            return HttpResponse('Ты постишь слишком часто, притормози.',
                                content_type='text/html')
        else:
            form = Post_Form(request.POST, request.FILES)
            if form.is_valid():
                current_thread = Thread.objects.get(pk=pk)
                post_op = False
                if form.cleaned_data['op']:
                    if current_thread.thread_op == request.session.get(sid, '') != '':
                        post_op = True                       
                post_text = form.cleaned_data['post_text']
                post_media = form.cleaned_data['post_media']
                sage = form.cleaned_data['sage']
                post_responses = form.cleaned_data['post_res']            
                if post_responses:
                    list_post_responses = post_responses.split(' ')
                    post_responses = [] 
                    for i in list_post_responses:
                        if i in post_text:
                            post_responses.append(i)
                Post.objects.create_post(post_thread=current_thread, post_text=post_text,
                                         post_media=post_media, sage=sage, op=post_op,
                                         responses=post_responses)
                response = HttpResponse('ok', content_type='text/html')
                response.set_cookie('poster', 'true', 30)
                return response
            else:
                return HttpResponse('Что ты делаешь, Карасик, не надо так',
                                    content_type='text/html')
    else:
        form = Post_Form()
        return render(request, 'includes/b_post_form.html', {'form': form})


def show_view(request, id):
    """
    Метод отдает пост, или тред в ответ на ajax запрос
    """
    post, thread = None, None
    try:
        post = Post.objects.get(post_id=id)
    except:
        pass
    try:    
        thread = Thread.objects.get(thread_id=id)
    except:
        pass
    if post:
        return render(request, 'includes/b_pop_post.html', {'qs': post})
    elif thread:
        return render(request, 'includes/b_pop_post.html', {'qs': thread})
    else:
        return HttpResponse('404, пост не найден', content_type='text/html')


class Faq_View(TemplateView):
    """
    Простой класс рендерящий страницу с примерами разметки текста

    в контекст дату передаются BBcode теги 
    """
    template_name = 'b_faq.html'   
    
    def get_context_data(self, **kwargs):
        context = super(Faq_View, self).get_context_data(**kwargs)
        context['s'] = '[s]Зачеркнутый текст[/s]'
        context['b'] = '[b]Жирный текст[/b]'
        context['u'] = '[u]Подчеркнутый текст[/u]'
        context['i'] = '[i]Курсивный текст[/i]'
        context['green'] = '[>>]Зеленый текст[/>>]'
        context['spoiler'] = '[spoiler]Текст под спойлером[/spoiler]'
        return context
