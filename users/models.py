from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom user manager para o modelo User do CoopApp.
    Gerencia criação de usuários comuns, administradores e superusuários.
    """

    def create_user(self, username, password=None, **extra_fields):
        """Cria e salva um usuário comum (cooperado por padrão)."""
        if not username:
            raise ValueError('O campo username é obrigatório')

        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Role.COOPERATED)

        # Validação condicional para administradores
        if extra_fields.get('role') == User.Role.ADMIN:
            if not extra_fields.get('email'):
                raise ValueError('Email é obrigatório para administradores')
            if not extra_fields.get('full_name'):
                raise ValueError('Nome completo é obrigatório')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_admin_user(self, username, email, full_name, password=None, **extra_fields):
        """Cria e salva um usuário administrador (não superusuário)."""
        extra_fields.update({
            'role': User.Role.ADMIN,
            'email': email,
            'full_name': full_name,
            'is_staff': False,  # Administradores não acessam o admin
            'is_superuser': False  # Não é superusuário
        })
        return self.create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        """Cria e salva um superusuário (admin com todos os privilégios)."""
        # Pega dados interativamente se não fornecidos
        if 'email' not in extra_fields:
            extra_fields['email'] = input("Email (obrigatório para admin): ")
        if 'full_name' not in extra_fields:
            extra_fields['full_name'] = input("Nome completo: ")

        extra_fields.update({
            'role': User.Role.ADMIN,
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        })

        # Validações reforçadas
        if not extra_fields['email']:
            raise ValueError('Superuser deve ter um email')
        if not extra_fields['full_name']:
            raise ValueError('Superuser deve ter um nome completo')

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
    id = models.BigAutoField(
        primary_key=True,
        editable=False,
        verbose_name='ID'
    )

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
        unique=True,
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

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='users_users',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='users_users_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
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
    all_objects = models.Manager()

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

    def deactivate(self):
        """Desativa o usuário."""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])

    def activate(self):
        """Ativa o usuário."""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])

    def get_full_name(self):
        """Retorna o nome completo."""
        return self.full_name

    def get_short_name(self):
        """Retorna nome curto (primeiro nome)."""
        return self.full_name.split()[0] if self.full_name else self.username
