import os
import sys
import django.core.handlers.wsgi

sys.path.append('/home/swvist/codes/teammetrics')
sys.path.append('/home/swvist/codes/teammetrics/web')

os.environ['DJANGO_SETTINGS_MODULE'] = 'web.settings'

application = django.core.handlers.wsgi.WSGIHandler()
