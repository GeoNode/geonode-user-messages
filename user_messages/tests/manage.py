import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

if __name__ == "__main__":
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['user_messages'])
    if failures:
        sys.exit(failures)
