





def set_base_template(request):
    if request.user.user_type == 'Admin':
        template = 'base_templates/admin-base.html'
    elif request.user.user_type == 'User':
        template = 'base_templates/user-base.html'
    else:
        template = 'base.html'
    return template