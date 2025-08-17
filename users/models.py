from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from common.models import Region


class UserManager(BaseUserManager):
    """
    Custom user manager para o modelo User do CoopApp.
    Gerencia criação de usuários comuns, administradores e superusuários.
    """

    def create_user(self, username, password=None, is_superuser=False, **extra_fields):
        """Cria e salva um usuário comum (cooperado por padrão)."""
        extra_fields['is_superuser'] = is_superuser

        if not username:
            raise ValueError('O campo username é obrigatório')

        # Nome completo obrigatório (menos para superuser)
        if not is_superuser:
            if not extra_fields.get('full_name'):
                raise ValueError('Nome completo é obrigatório')

        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_cooperated', True)
        extra_fields.setdefault('is_admin', False)
        extra_fields.setdefault('is_staff', False)

        # Validação condicional para administradores
        if extra_fields.get('is_admin'):
            if not extra_fields.get('email'):
                user_type = 'superusuários' if is_superuser else 'administradores'
                raise ValueError(f'Email é obrigatório para {user_type}')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)

        if not is_superuser:
            user.full_clean()

        user.save(using=self._db)
        return user

    def create_admin_user(self, username, email, full_name, password=None, **extra_fields):
        """Cria e salva um usuário administrador (não superusuário)."""
        extra_fields.update(
            {
                'is_admin': True,
                'is_cooperated': True,
                'email': email,
                'full_name': full_name,
                'is_staff': False,  # Administradores não acessam o admin
                'is_superuser': False,  # Não é superusuário
            }
        )
        return self.create_user(username, password, **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Cria e salva um superusuário."""

        # Validações obrigatórias
        if not email:
            raise ValueError('Superuser deve ter um email')

        # Configurações obrigatórias para superuser
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_cooperated', False)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # Validações do Django
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True')

        # Adiciona email aos extra_fields
        extra_fields['email'] = email

        return self.create_user(username, password, **extra_fields)


class CooperatedUserManager(models.Manager):
    """Manager específico para usuários cooperados (para a interface gráfica)."""

    def get_queryset(self):
        """Retorna apenas usuários cooperados ativos por padrão."""
        return super().get_queryset().filter(is_cooperated=True, is_active=True)


class AdminUserManager(models.Manager):
    """Manager específico para usuários Admin ativos (para a interface gráfica)."""

    def get_queryset(self):
        """Retorna apenas usuários ativos por padrão."""
        return super().get_queryset().filter(is_admin=True, is_active=True)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuário customizado para o CoopApp.
    Representa tanto administradores quanto cooperados do sistema.
    """

    username = models.CharField(
        'Nome de usuário',
        max_length=150,
        unique=True,
        help_text='Nome único para login no sistema',
    )

    password = models.CharField('Senha', max_length=128, help_text='Senha criptografada')

    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )

    email = models.EmailField(
        'Email',
        blank=True,
        null=True,
        unique=True,
        help_text='Email obrigatório para administradores',
    )

    full_name = models.CharField(
        'Nome completo', max_length=255, blank=True, help_text='Nome completo do usuário'
    )

    is_admin = models.BooleanField(
        'Administrador', default=False, help_text='Usuário com permissões administrativas'
    )

    is_cooperated = models.BooleanField(
        'Cooperado',
        default=True,
        help_text='Usuário participante das operações da cooperativa',
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

    updated_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_users',
        verbose_name='Atualizado por',
        help_text='Administrador que realizou a última atualização',
    )

    # Configurações do Django
    objects = UserManager()
    admin = AdminUserManager()
    cooperated = CooperatedUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

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
        if self.is_admin and self.created_by and not self.created_by.is_admin:
            raise ValidationError(
                {'created_by': 'Apenas administradores podem criar outros administradores'}
            )

        # Email obrigatório para admins
        if self.is_admin and not self.email:
            raise ValidationError({'email': 'Email é obrigatório para administradores'})

        # Nome completo obrigatório (menos para superuser)
        if not self.is_superuser and not self.full_name:
            raise ValidationError({'full_name': 'Nome completo é obrigatório'})

    def save(self, *args, **kwargs):
        """Override do save para executar validações."""
        if not getattr(self, 'is_superuser', False):
            self.full_clean()
        super().save(*args, **kwargs)

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
