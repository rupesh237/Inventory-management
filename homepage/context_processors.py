from .models import Company

def company_name(request):
    company = None
    if request.user.is_authenticated:
        user_branch = request.user.profile.branch
        company = user_branch.company
    return {'company': company}