"""
Celery configuration for Job Agent System

This module provides Celery setup for background tasks such as:
- CV processing
- Job search and analysis
- Email notifications
- Data synchronization
- Periodic tasks
"""

import os
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    'job_agent',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=['app.tasks']
)

# Celery configuration
celery_app.conf.update(
    # Task configuration
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'app.tasks.process_cv': {'queue': 'cv_processing'},
        'app.tasks.search_jobs': {'queue': 'job_search'},
        'app.tasks.send_email': {'queue': 'email'},
        'app.tasks.generate_recommendations': {'queue': 'recommendations'},
    },
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # Result backend configuration
    result_expires=3600,  # 1 hour
    
    # Security
    task_send_sent_event=True,
    task_track_started=True,
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_acks_on_failure_or_timeout=True,
)

# Periodic tasks configuration
celery_app.conf.beat_schedule = {
    'cleanup-old-cvs': {
        'task': 'app.tasks.cleanup_old_cvs',
        'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM
    },
    'update-job-listings': {
        'task': 'app.tasks.update_job_listings',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'generate-user-recommendations': {
        'task': 'app.tasks.generate_user_recommendations',
        'schedule': crontab(minute=0, hour=9),  # Daily at 9 AM
    },
    'cleanup-expired-sessions': {
        'task': 'app.tasks.cleanup_expired_sessions',
        'schedule': crontab(minute=0, hour=1),  # Daily at 1 AM
    },
    'sync-external-jobs': {
        'task': 'app.tasks.sync_external_jobs',
        'schedule': crontab(minute=30, hour='*/4'),  # Every 4 hours at 30 minutes past
    },
    'send-daily-digest': {
        'task': 'app.tasks.send_daily_digest',
        'schedule': crontab(minute=0, hour=8),  # Daily at 8 AM
    },
    'cleanup-old-matches': {
        'task': 'app.tasks.cleanup_old_matches',
        'schedule': crontab(minute=0, hour=3, day_of_week=0),  # Weekly on Sunday at 3 AM
    },
    'update-analytics': {
        'task': 'app.tasks.update_analytics',
        'schedule': crontab(minute=0, hour=0),  # Daily at midnight
    },
}

# Queue configuration
celery_app.conf.task_queues = {
    'cv_processing': {
        'exchange': 'cv_processing',
        'routing_key': 'cv_processing',
    },
    'job_search': {
        'exchange': 'job_search',
        'routing_key': 'job_search',
    },
    'email': {
        'exchange': 'email',
        'routing_key': 'email',
    },
    'recommendations': {
        'exchange': 'recommendations',
        'routing_key': 'recommendations',
    },
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
}

# Error handling and monitoring
celery_app.conf.task_annotations = {
    'app.tasks.*': {
        'rate_limit': '10/m',  # 10 tasks per minute
        'time_limit': 300,  # 5 minutes timeout
        'soft_time_limit': 240,  # 4 minutes soft timeout
        'max_retries': 3,
        'retry_backoff': True,
        'retry_backoff_max': 300,  # 5 minutes
        'retry_jitter': True,
    }
}

# Custom task base class
class BaseTask(celery_app.Task):
    """Base class for all tasks with common functionality"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        from app.core.logging import get_logger
        
        logger = get_logger(__name__)
        logger.error(
            f"Task {self.name} failed",
            extra={
                "task_id": task_id,
                "args": args,
                "kwargs": kwargs,
                "error": str(exc),
                "traceback": str(einfo)
            }
        )
        
        # Send error notification (in production)
        # self.send_error_notification(exc, task_id, args, kwargs)
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        from app.core.logging import get_logger
        
        logger = get_logger(__name__)
        logger.info(
            f"Task {self.name} completed successfully",
            extra={
                "task_id": task_id,
                "args": args,
                "kwargs": kwargs,
                "result": str(retval)[:200]  # Truncate long results
            }
        )
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry"""
        from app.core.logging import get_logger
        
        logger = get_logger(__name__)
        logger.warning(
            f"Task {self.name} retrying",
            extra={
                "task_id": task_id,
                "args": args,
                "kwargs": kwargs,
                "error": str(exc)
            }
        )
    
    def send_error_notification(self, exc, task_id, args, kwargs):
        """Send error notification (placeholder for production)"""
        # In production, this could send an email, Slack notification, etc.
        pass

# Set custom task base class
celery_app.Task = BaseTask

# Health check task
@celery_app.task(bind=True, name='health.check')
def health_check(self):
    """Health check task for monitoring"""
    return {
        "status": "healthy",
        "timestamp": self.request.timestamp,
        "worker": self.request.hostname
    }

# Example of a simple task for testing
@celery_app.task(bind=True, name='test.task')
def test_task(self, x, y):
    """Test task for Celery functionality"""
    result = x + y
    return {
        "result": result,
        "task_id": self.request.id,
        "worker": self.request.hostname
    }