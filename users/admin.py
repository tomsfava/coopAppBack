from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Configuração da interface de administração para o modelo User.
    Ajusta a exibição e os campos de formulário para o modelo customizado.
    """

    # O campo 'username' já está definido como USERNAME_FIELD
    # O campo 'password' já é gerenciado pelo BaseUserAdmin

    # Campos que serão exibidos na lista de usuários no admin
    list_display = (
        'username',
        'full_name',
        'role',
        'is_active',
        'is_staff',
        'date_joined',
    )

    # Campos que podem ser usados para filtrar a lista
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'role', 'date_joined')

    # Campos que podem ser usados para pesquisa
    search_fields = ('username', 'full_name', 'email')

    # Campos de formulário para adição e edição de usuários
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('full_name', 'email', 'role')}),
        (
            'Permissões',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Auditoria', {'fields': ('created_by',)}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined', 'updated_at')}),
    )

    # Campos somente para leitura na interface de edição
    readonly_fields = ('last_login', 'date_joined', 'updated_at')

    # Adiciona os campos 'full_name' e 'role' para a tela de criação de usuário
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'password', 'full_name', 'email', 'role'),
            },
        ),
    )
