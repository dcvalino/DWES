from rest_framework.permissions import BasePermission

class IsOrganizador(BasePermission):
    """
    Permiso que permite el acceso solo a usuarios cuyo campo 'tipo' es 'organizador'.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'tipo') and request.user.tipo.lower() == 'organizador'

class IsParticipante(BasePermission):
    """
    Permiso que permite el acceso solo a usuarios cuyo campo 'tipo' es 'asistente' o 'participante'.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'tipo') and request.user.tipo.lower() in ['asistente', 'participante']
