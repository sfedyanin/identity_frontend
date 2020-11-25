import rules
import logging

logger = logging.getLogger('vdx_id.%s' % __name__)


#----------------
# Predicates
#----------------
@rules.predicate
def is_data_owner(user, access_object):
    if access_object and user:
        logger.info("Checking Id(%s) is data-owner of Grp(%s) "
                    % (user, access_object))
        return user.associated_identity in access_object.owners.all()
    return False


@rules.predicate
def is_admin(user):
    if user:
        return user.is_superuser
    return False

# is_operator = rules.is_group_member('operators')

# Rules
rules.add_rule('data_owner_approval', is_data_owner | is_admin)

# Permissions
rules.add_perm('id_access.change_access_group', is_data_owner | is_admin)

# Get suggested authorities (return a list of pks)
def data_owner_approval_suggestions(access_object):
    from id_users.models import VdxIdUser
    admin_ids = VdxIdUser.objects.filter(
        is_superuser=True).values_list(
            'associated_identity__pk', flat=True)
    access_owners = access_object.owners.all().values_list(
        'pk', flat=True)
    return list(admin_ids) + list(access_owners)