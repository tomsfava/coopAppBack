from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom user manager para o modelo User do CoopApp.
    Gerencia criação de usuários comuns e superusuários.
    """

    def create_user(self, username, password=None, **extra_fields):
        """Cria e salva um usuário comum."""
        if not username:
            raise ValueError('O campo username é obrigatório')
        # Define valores padrão
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Role.COOPERATED)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """Cria e salva um superusuário (admin)."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True')

        return self.create_user(username, password, **extra_fields)

    def get_queryset(self):
        """Retorna apenas usuários ativos por padrão."""
        return super().get_queryset().filter(is_active=True)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuário customizado para o CoopApp.
    Representa tanto administradores quanto cooperados do sistema.
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        COOPERATED = 'COOPERATED', 'Cooperado'

    # Campos principais
    username = models.CharField(
        'Nome de usuário',
        max_length=150,
        unique=True,
        help_text='Nome único para login no sistema',
    )

    password = models.CharField('Senha', max_length=128, help_text='Senha criptografada')

    email = models.EmailField(
        'Email',
        blank=True,
        null=True,
        help_text='Email opcional, usado principalmente por administradores',
    )

    full_name = models.CharField(
        'Nome completo', max_length=255, help_text='Nome completo do usuário'
    )

    role = models.CharField(
        'Papel',
        max_length=20,
        choices=Role.choices,
        default=Role.COOPERATED,
        help_text='Papel do usuário no sistema',
    )

    # Campos de controle
    is_active = models.BooleanField(
        'Ativo', default=True, help_text='Indica se o usuário pode fazer login no sistema'
    )

    is_staff = models.BooleanField(
        'Membro da equipe',
        default=False,
        help_text='Indica se o usuário pode acessar o admin',
    )

    # Timestamps
    date_joined = models.DateTimeField(
        'Data de cadastro', default=timezone.now, help_text='Data e hora do cadastro'
    )

    updated_at = models.DateTimeField(
        'Última atualização', auto_now=True, help_text='Data e hora da última atualização'
    )

    # Auditoria
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        verbose_name='Criado por',
        help_text='Administrador que realizou o cadastro',
    )

    # Configurações do Django
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'users_user'
        ordering = ['full_name']

    def __str__(self):
        """Retorna representação string do usuário."""
        return self.full_name or self.username

    def clean(self):
        """Validações customizadas."""
        super().clean()

        # Validações de role vs created_by
        if (
            self.role == self.Role.ADMIN
            and self.created_by
            and self.created_by.role != self.Role.ADMIN
        ):
            raise ValidationError(
                {'created_by': 'Apenas administradores podem criar outros administradores'}
            )

        # Email obrigatório para admins
        if self.role == self.Role.ADMIN and not self.email:
            raise ValidationError({'email': 'Email é obrigatório para administradores'})

    def save(self, *args, **kwargs):
        """Override do save para executar validações."""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_admin(self):
        """Verifica se é administrador."""
        return self.role == self.Role.ADMIN

    @property
    def is_cooperated(self):
        """Verifica se é cooperado."""
        return self.role == self.Role.COOPERATED

    def get_full_name(self):
        """Retorna o nome completo."""
        return self.full_name

    def get_short_name(self):
        """Retorna nome curto (primeiro nome)."""
        return self.full_name.split()[0] if self.full_name else self.username
