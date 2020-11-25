import logging
from rest_framework import permissions

logger = logging.getLogger("%s" % __name__)


class IsOwnIdentityOrAdmin(permissions.BasePermission):

    # 'has_object_permission()' not suitable for POST
    def has_permission(self, request, view):
        if request.method in ["HEAD", "GET"]:
            return True
        logger.info("Checking object permission")
        if not request.user.is_authenticated:
            logger.info("Not authenticated")
            return False
        if request.user.is_superuser:
            logger.info("Is Admin")
            return True
        user_ident = getattr(
            request.user.associated_identity, 'unique_identifier')
        identity_id = request.data.get('identity')
        logger.info("U(%s) I(%s)" % (user_ident, identity_id))
        return identity_id is not None and identity_id == user_ident
