# panel/utils.py
#reffrral link generation

from .models import Respondent


def get_referrer_from_session(request):
    """
    Reads referral code from session.
    Returns Respondent object or None.
    """
    code = request.session.get('referral_code')
    if code:
        try:
            return Respondent.objects.get(referral_code=code)
        except Respondent.DoesNotExist:
            return None
    return None