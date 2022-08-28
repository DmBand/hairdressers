from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """ Открывает доступ только владельцу """

    def has_object_permission(self, request, view, obj):
        return obj.username == request.user.username


class IsHairdresserOwner(permissions.BasePermission):
    """ Открывает доступ только владельцу (для парикмахеров) """

    def has_object_permission(self, request, view, obj):
        return obj.owner.username == request.user.username
