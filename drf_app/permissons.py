from rest_framework import permissions


# class IsOwner(BasePermission):
#     def has_permission(self, request, view):
#         # если метод безопасный, то доступ у всех пользователей
#         if request.method in SAFE_METHODS:
#             return True
#         return bool(request.user == )


class IsOwner(permissions.BasePermission):
    """ Открывает доступ только владельцу """
    def has_object_permission(self, request, view, obj):
        return obj.username == request.user.username


class IsHairdresserOwner(permissions.BasePermission):
    """ Открывает доступ только владельцу (для парикмахеров) """
    def has_object_permission(self, request, view, obj):
        return obj.owner.username == request.user.username
