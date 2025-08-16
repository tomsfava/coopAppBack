# Arquivo: users/management/commands/createsuperuser.py

import getpass
import sys

from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management import CommandError


class Command(BaseCommand):
    """
    Comando customizado para criar superusuários com email obrigatório
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove email dos REQUIRED_FIELDS para evitar conflitos
        if hasattr(self.UserModel, 'REQUIRED_FIELDS'):
            self.UserModel.REQUIRED_FIELDS = [
                f for f in self.UserModel.REQUIRED_FIELDS if f != 'email'
            ]

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--email',
            help='Email do superusuário',
        )

    def handle(self, *args, **options):
        """
        Handle principal que sobrescreve o comportamento padrão
        """
        username = options.get('username')
        email = options.get('email')
        database = options.get('database')

        user_data = {}
        verbose_field_name = self.username_field.verbose_name

        try:
            # Pede username se não foi fornecido
            if not username:
                message = f'{verbose_field_name}'
                if self.username_field.blank:
                    message += (
                        f' (deixe em branco para usar {self.username_field.default!r})'
                    )
                message += ': '
                username = self.get_input_data(self.username_field, message)
                if not username:
                    username = self.username_field.default

            user_data[self.UserModel.USERNAME_FIELD] = username

            # Valida se username já existe
            if (
                self.UserModel._default_manager.db_manager(database)
                .filter(**{self.UserModel.USERNAME_FIELD: username})
                .exists()
            ):
                raise CommandError(
                    f'Erro: Um usuário com este {verbose_field_name} já existe.'
                )

            # Pede email se não foi fornecido
            if not email:
                email = input('Email: ')

            # Valida email
            if not email:
                raise CommandError('Email é obrigatório para superusuários.')

            user_data['email'] = email

            # Valida se email já existe
            if (
                self.UserModel._default_manager.db_manager(database)
                .filter(email=email)
                .exists()
            ):
                raise CommandError('Erro: Um usuário com este email já existe.')

            # Pede senha
            password = None
            if not options.get('verbosity', 1) == 0:
                password = getpass.getpass('Password: ')
                if password:
                    password2 = getpass.getpass('Password (again): ')
                    if password != password2:
                        raise CommandError('Erro: As senhas não coincidem.')

            # Valida senha
            if password:
                try:
                    validate_password(password)
                except ValidationError as e:
                    errors = '\n'.join(e.messages)
                    response = input(
                        f'This password {errors.lower()}\n'
                        f'Bypass password validation and create user anyway? [y/N]: '
                    )
                    if response.lower() != 'y':
                        raise CommandError('Superusuário não foi criado.')  # noqa: B904

            # Cria o superusuário
            user_data['password'] = password

            self.UserModel._default_manager.db_manager(database).create_superuser(
                username=username, email=email, password=password
            )

            if options.get('verbosity', 1) >= 1:
                self.stdout.write('Superusuário criado com sucesso.')

        except KeyboardInterrupt:
            self.stderr.write('\nOperação cancelada.')
            sys.exit(1)
        except Exception as e:
            raise CommandError(f'Erro ao criar superusuário: {e}')  # noqa: B904

    def get_input_data(self, field, message, default=None):
        """
        Método auxiliar para obter dados de entrada
        """
        raw_value = input(message)
        if not raw_value and default:
            raw_value = default
        return raw_value
