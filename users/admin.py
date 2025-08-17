from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User


class UserAdmin(BaseUserAdmin):
    """
    Configuração da interface de administração para o modelo User.
    Ajusta a exibição e os campos de formulário para o modelo customizado.
    """

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    # Campos que serão exibidos na lista de usuários no admin
    list_display = (
        'username',
        'full_name',
        'email',
        'region',
        'is_admin',
        'is_cooperated',
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
    )

    # Campos que podem ser usados para filtrar a lista
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'is_admin',
        'is_cooperated',
        'region',
        'date_joined',
    )

    # Campos que podem ser usados para pesquisa
    search_fields = ('username', 'full_name', 'email', 'region__name')

    # Campos de formulário para adição e edição de usuários
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('full_name', 'email', 'region')}),
        (
            'Permissões',
            {
                'fields': (
                    'is_admin',
                    'is_cooperated',
                    'is_active',
                )
            },
        ),
        ('Auditoria', {'fields': ('created_by', 'updated_by')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined', 'updated_at')}),
    )

    # Campos somente para leitura na interface de edição
    readonly_fields = (
        'last_login',
        'date_joined',
        'updated_at',
        'created_by',
        'updated_by',
    )

    # Campos exibidos na tela de criação de usuário
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'password',
                    'full_name',
                    'email',
                    'region',
                    'is_admin',
                    'is_cooperated',
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        """Preenche created_by e updated_by automaticamente."""
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        if change:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)
