def pending_approvals(request):
    if request.user and getattr(request.user, 'associated_identity', None):
        auth_attention = request.user.associated_identity.auth_attention
        return {
            'pending_approvals': auth_attention.filter(processing=True).count()}
    else:
        return {}