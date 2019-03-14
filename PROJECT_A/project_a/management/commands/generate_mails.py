import tempfile
import sys

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Q
from django.utils.timezone import now
from django.template.loader import render_to_string

from post_office.lockfile import FileLock, FileLocked
from post_office.mail import send_queued
from post_office.models import Email, STATUS
from post_office.logutils import setup_loghandlers
from post_office import mail



logger = setup_loghandlers()
default_lockfile = tempfile.gettempdir() + "/post_office"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-p', '--processes',
            type=int,
            default=1,
            help='Number of processes used to send emails',
        )
        parser.add_argument(
            '-L', '--lockfile',
            default=default_lockfile,
            help='Absolute path of lockfile to acquire',
        )
        parser.add_argument(
            '-l', '--log-level',
            type=int,
            help='"0" to log nothing, "1" to only log errors',
        )

    def handle(self, *args, **options):
        logger.info('Acquiring lock for sending queued emails at %s.lock' %
                    options['lockfile'])
        mail.send(
            ['pramod@headrun.com'], # List of email addresses also accepted
            'pramod.ece091@gmail.com',
            subject='Welcome!',
            html_message=render_to_string('project_a/test.html', {'data':{'Ashok':[('Band', 1),\
                ('Tood', 2)],'Khan': [('Mat', 6),('Rat', 7)], 'Ash': [('Cool', 3) , ('Float', 4), ('Loop', 5)]}}),
            # scheduled_time=date(2014, 1, 1),
            headers={'Reply-to': 'reply@example.com', 'Content-Type':'text/html'},
            context={'name': 'Alice'},
        )         
        try:
            with FileLock(options['lockfile']):

                while 1:
                    try:
                        send_queued(options['processes'],
                                    options.get('log_level'))
                    except Exception as e:
                        logger.error(e, exc_info=sys.exc_info(),
                                     extra={'status_code': 500})
                        raise

                    # Close DB connection to avoid multiprocessing errors
                    connection.close()

                    if not Email.objects.filter(status=STATUS.queued) \
                            .filter(Q(scheduled_time__lte=now()) | Q(scheduled_time=None)).exists():
                        break
        except FileLocked:
            logger.info('Failed to acquire lock, terminating now.')