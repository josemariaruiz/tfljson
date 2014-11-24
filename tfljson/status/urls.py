from django.conf.urls import patterns, url

urlpatterns = patterns('status.views',
    url(r'status/$', 'status', name='status_status'),
    url(r'$', 'index', name='status_index'),
)
