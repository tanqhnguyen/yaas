from django.core.management.base import BaseCommand, CommandError
from authentication.forms import RegistrationForm

class Command(BaseCommand):
    args = '<Number of user>'
    help = 'Generate a bunch of users'

    def handle(self, *args, **options):
        if len(args) == 0:
            count = 50
        else:
            count = args[0]
            
        for x in range(0, int(count)):
            data = {
                'username': 'test_user_%s' % x,
                'password1': 'test_password_%s' % x,
                'password2': 'test_password_%s' % x,
                'email': 'testemail%s@localhost.local' % x
            }
            form = RegistrationForm(data)
            if form.is_valid():
                user = form.save(True)
                self.stdout.write('Sucessfully created user id %s' % user.id)
