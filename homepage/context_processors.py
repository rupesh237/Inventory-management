from .models import Company

def company_name(request):
    user_branch = request.user.profile.branch
    company = user_branch.company
    return {
        'company': company
    }