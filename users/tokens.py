from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):

    key_salt = "users.tokens.EmailVerificationTokenGenerator"


email_verification_token = EmailVerificationTokenGenerator()