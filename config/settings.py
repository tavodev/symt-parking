from split_settings.tools import optional, include

include(
    'components/base.py',
    'components/database.py',
    'components/auth.py',
    'components/email.py',

    optional('local_settings.py')
)