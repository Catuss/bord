from django.conf.urls import url
from . import views 

urlpatterns = [
    url(r'^$', views.Thread_List_View.as_view(), name='list_thread'),
    url(r'^(?P<pk>[0-9]+)/$', views.Thread_Detail_view.as_view(), name='detail_thread'),
    url(r'^faq/$', views.Faq_View.as_view(), name='faq'),
    url(r'^complaint/$', views.complaint_view, name='complaint'),
    url(r'^posting/(?P<pk>[0-9]+)/$', views.posting_view, name='posting'),
    url(r'^show/(?P<id>[0-9]+)/$', views.show_view, name='showing'),
    url(r'^update/(?P<pk>[0-9]+)/$', views.Update_List_Post_View.as_view(), name='update_list'),
]
