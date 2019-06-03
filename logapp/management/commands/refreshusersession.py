import argparse

from django.core.management.base import BaseCommand
from django.utils import timezone

from logapp.models import UserActions, UserSession, UserSessionStats


class User():

    def __init__(self, user_obj, command_instance):
        self.command_instance = command_instance
        self.user_obj = user_obj
        self.session_number = 0
        self.last_session = None
        self.max_session_duration = timezone.timedelta()
        self.min_session_duration = timezone.timedelta(days=100)
        self.avg_session_duration = timezone.timedelta()
        self.activities = []

    def add_activity(self, activity):
        self.activities.append(activity)

    def calculate_metrics(self, time_windows_in_sec):
        self.session_number = 0
        self.last_session = self.activities[0][0]
        start_session = self.activities[0][0]
        previous_timestamp = self.activities[0][0]
        sessions = []

        for index, activity in enumerate(self.activities):
            timestamp = activity[0]

            diff_in_secs = (timestamp - previous_timestamp).total_seconds()
            if diff_in_secs > time_windows_in_sec or index == len(self.activities) - 1:
                duration = previous_timestamp.replace(microsecond=0) - start_session.replace(microsecond=0)

                self.command_instance.stdout.write(
                    self.command_instance.style.SUCCESS(
                        '{0} {1} {2} {3}'.format(self.user_obj, start_session, previous_timestamp, duration)))
                UserSession.objects.create(user=self.user_obj, start_time=start_session, end_time=previous_timestamp,
                                           duration=duration)

                if duration > self.max_session_duration:
                    self.max_session_duration = duration
                if duration < self.min_session_duration:
                    self.min_session_duration = duration
                sessions.append(duration)
                self.last_session = previous_timestamp
                self.session_number += 1
                start_session = timestamp

            previous_timestamp = timestamp

        self.avg_session_duration = sum(sessions, timezone.timedelta()) / len(sessions)
        # remove microseconds
        self.avg_session_duration = self.avg_session_duration - timezone.timedelta(
            microseconds=self.avg_session_duration.microseconds)

    def create_session_stats(self):
        UserSessionStats.objects.create(user=self.user_obj, session_number=self.session_number,
                                        last_session_timestamp=self.last_session,
                                        max_session_duration=self.max_session_duration,
                                        min_session_duration=self.min_session_duration,
                                        avg_session_duration=self.avg_session_duration)


def valid_date(s):
    try:
        return timezone.make_aware(timezone.datetime.strptime(s, "%Y-%m-%d"))
    except ValueError:
        msg = "'{0}' is not a valid date".format(s)
        raise argparse.ArgumentTypeError(msg)


class Command(BaseCommand):
    help = 'It calculates user sessions'

    def add_arguments(self, parser):
        parser.add_argument('start_date', type=valid_date, help='lower time bound')
        parser.add_argument('end_date', type=valid_date, help='upper time bound')
        parser.add_argument('--session-gap', default=15, type=int, help='time between in two sessions (in minutes)')
        parser.add_argument('--delete-previous', action='store_true', help='delete previous sessions')

    def handle(self, *args, **options):
        start_date = options['start_date']
        end_date = options['end_date']
        session_gap = options['session_gap'] * 60
        delete_previous = options['delete_previous']

        if delete_previous:
            UserSession.objects.all().delete()
            UserSessionStats.objects.all().delete()

        users = dict()
        url_set = set()
        for user_action_obj in UserActions.objects.select_related('user').filter(
                timestamp__range=(start_date, end_date)):
            # it is not relevant admin data
            url = user_action_obj.url.split('?')[0]
            timestamp = user_action_obj.timestamp
            username = user_action_obj.user.username

            # if url.startswith('/admin'):
            #    continue
            # actividades no relevantes
            if url in ['/favicon.ico', '/', '/admin/datamanager/latestJobChanges/']:
                continue

            if username not in users:
                users[username] = User(user_action_obj.user, self)

            users[username].add_activity([timestamp])

        for username in users:
            user = users[username]
            user.calculate_metrics(session_gap)
            user.create_session_stats()
