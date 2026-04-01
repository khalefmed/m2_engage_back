import os
from celery import Celery

# Définir les réglages Django par défaut pour celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('marketing_platform')

# Utiliser une chaîne ici pour que le worker n'ait pas à sérialiser
# l'objet de configuration lors de l'utilisation de Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Charger les tâches de toutes les applications inscrites
app.autodiscover_tasks()