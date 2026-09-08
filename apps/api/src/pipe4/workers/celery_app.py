from celery import Celery
from pipe4.config import get_settings
settings=get_settings()
celery_app=Celery('pipe4',broker=settings.redis_url,backend=settings.redis_url,include=['pipe4.workers.tasks'])
celery_app.conf.update(task_serializer='json',accept_content=['json'],result_serializer='json',timezone='UTC',enable_utc=True,task_acks_late=True,worker_prefetch_multiplier=1,task_reject_on_worker_lost=True,broker_connection_retry_on_startup=True)
celery_app.conf.beat_schedule={
    'pipe4-expire-states-every-minute':{'task':'pipe4.expire_states','schedule':60.0},
    'pipe4-dispatch-outbox-recovery':{'task':'pipe4.dispatch_outbox','schedule':10.0},
}
