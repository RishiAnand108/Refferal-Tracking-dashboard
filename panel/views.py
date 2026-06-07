# panel/views.py
#refferal tracking view
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Respondent, Survey, ReferralStatus
from .utils import get_referrer_from_session

# panel/views.py — add this view
from .forms import SignupForm

def signup_view(request):
    referrer      = get_referrer_from_session(request)
    referrer_name = request.session.get('referrer_name', '')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            respondent = form.save(commit=False)

            # auto-link referrer
            if referrer:
                respondent.referred_by = referrer

            respondent.save()

            # create referral status — lead stage
            if referrer:
                ReferralStatus.objects.create(
                    referrer     = referrer,
                    referred     = respondent,
                    stage        = 'lead',
                    bonus_amount = 50.00
                )

            # set cooloff
            respondent.set_cooloff()

            # clear session
            request.session.pop('referral_code', None)
            request.session.pop('referrer_name', None)

            messages.success(
                request,
                f'Welcome {respondent.name}! '
                f'Your unique ID is {respondent.unique_id}.'
            )
            return redirect('dashboard')
    else:
        form = SignupForm()

    return render(request, 'panel/signup.html', {
        'form':          form,
        'referrer_name': referrer_name,
    })


def track_referral(request, referral_code):
    """
    When someone clicks a referral link:
    /refer/<referral_code>/
    Store the referral code in session and
    redirect to signup page.
    """
    try:
        referrer = Respondent.objects.get(
            referral_code=referral_code
        )
        # store in session — persists even if browser closed
        request.session['referral_code'] = str(referral_code)
        request.session['referrer_name'] = referrer.name
        messages.info(
            request,
            f'You were referred by {referrer.name}. '
            f'Complete signup to help them earn a bonus!'
        )
    except Respondent.DoesNotExist:
        messages.warning(request, 'Invalid referral link.')

    return redirect('signup')