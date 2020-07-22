from rest_framework import permissions


def has_collection_permission(request, collection):
    if request.method in permissions.SAFE_METHODS:
        if collection.is_public or request.user in collection.viewers:
            return True
    return request.user in collection.owners


class HasCollectionPermissionOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return has_collection_permission(request, obj)


class HasSubCollectionPermissionOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return has_collection_permission(request, obj.collection)
