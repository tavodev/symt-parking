AUTH_USER_MODEL = 'accounts.CustomUser'

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

ACCOUNT_LOGIN_METHODS = {'email'}  # Login con email en lugar de username
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']  # Email obligatorio, sin username
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # Verificación de email obligatoria
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/5m',  # 5 intentos fallidos cada 5 minutos
}
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True  # Logout al cambiar contraseña

ACCOUNT_FORMS = {
    'signup': 'accounts.forms.UserRegistrationForm',  # Tu formulario personalizado
}

LOGIN_REDIRECT_URL = '/'  # Después del login
LOGOUT_REDIRECT_URL = '/'  # Después del logout
ACCOUNT_LOGOUT_REDIRECT_URL = '/'  # Después del logout
