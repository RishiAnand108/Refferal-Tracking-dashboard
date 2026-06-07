# panel/views.py
#refferal tracking view
import csv
import openpyxl
from django.http import HttpResponse
import json


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Respondent, Survey, ReferralStatus
from .utils import get_referrer_from_session
# panel/views.py — add this
from django.contrib.admin.views.decorators import staff_member_required
# panel/views.py — add this
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.admin.views.decorators import staff_member_required
# panel/views.py — add this
from .forms import AddRespondentForm

# panel/views.py — add this
from django.views.decorators.csrf import csrf_exempt

def ai_categorize(request):
    if request.method == 'POST':
        notes = request.POST.get('notes', '').lower()

        # Clean keyword-based stub
        # Replace with Claude API call in production
        keywords = {
            'Healthcare':  ['hospital', 'doctor', 'nurse',
                           'medical', 'clinic', 'health',
                           'pharma', 'patient', 'icu', 'ward'],
            'Finance':     ['bank', 'finance', 'insurance',
                           'investment', 'stock', 'loan',
                           'mutual fund', 'ca', 'accountant'],
            'Retail':      ['shop', 'store', 'mall', 'retail',
                           'sales', 'ecommerce', 'amazon',
                           'flipkart', 'merchant'],
            'FMCG':        ['fmcg', 'consumer', 'grocery',
                           'food', 'beverage', 'brand',
                           'hul', 'nestle', 'itc'],
            'Technology':  ['tech', 'software', 'developer',
                           'engineer', 'it', 'startup',
                           'coding', 'programmer', 'data'],
        }

        scores = {}
        for category, words in keywords.items():
            scores[category] = sum(
                1 for word in words if word in notes
            )

        best       = max(scores, key=scores.get)
        best_score = scores[best]

        if best_score == 0:
            best       = 'Other'
            confidence = 'low'
        elif best_score == 1:
            confidence = 'medium'
        else:
            confidence = 'high'

        return JsonResponse({
            'category':   best,
            'confidence': confidence,
            'reason':     f'Notes contain keywords associated '
                          f'with the {best} sector.',
            'stub_note':  'Connect Claude API for production use. '
                          'System prompt: Classify participant into '
                          'Healthcare/Finance/Retail/FMCG/Technology/Other '
                          'based on notes. Return JSON with category, '
                          'confidence, reason.'
        })

    return JsonResponse({'error': 'POST required'}, status=400)
@staff_member_required
def export_data(request):
    # get same filters as dashboard
    q               = request.GET.get('q', '')
    city_filter     = request.GET.get('city', '')
    category_filter = request.GET.get('category', '')
    fmt             = request.GET.get('format', 'csv')

    respondents = Respondent.objects.all()
    if q:
        respondents = respondents.filter(
            Q(name__icontains=q)      |
            Q(email__icontains=q)     |
            Q(unique_id__icontains=q) |
            Q(city__icontains=q)
        )
    if city_filter:
        respondents = respondents.filter(city=city_filter)
    if category_filter:
        respondents = respondents.filter(category=category_filter)

    if fmt == 'excel':
        # Excel export
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Respondents'
        ws.append([
            'Unique ID', 'Name', 'Email', 'Phone',
            'City', 'Category', 'Status',
            'Referred By', 'Cool-off Until', 'Date Joined'
        ])
        for r in respondents:
            ws.append([
                r.unique_id, r.name, r.email, r.phone,
                r.city, r.category, r.status,
                r.referred_by.name if r.referred_by else '',
                str(r.cool_off_until) if r.cool_off_until else '',
                str(r.date_joined.date())
            ])
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=respondents.xlsx'
        wb.save(response)
        return response

    else:
        # CSV export
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=respondents.csv'
        writer = csv.writer(response)
        writer.writerow([
            'Unique ID', 'Name', 'Email', 'Phone',
            'City', 'Category', 'Status',
            'Referred By', 'Cool-off Until', 'Date Joined'
        ])
        for r in respondents:
            writer.writerow([
                r.unique_id, r.name, r.email, r.phone,
                r.city, r.category, r.status,
                r.referred_by.name if r.referred_by else '',
                r.cool_off_until or '',
                r.date_joined.date()
            ])
        return response
@staff_member_required
def add_respondent(request):
    if request.method == 'POST':
        form = AddRespondentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Respondent added successfully.')
            return redirect('dashboard')
    else:
        form = AddRespondentForm()
    return render(request, 'panel/add_respondent.html', {'form': form})

@staff_member_required
def dashboard(request):
    q              = request.GET.get('q', '')
    city_filter    = request.GET.get('city', '')
    category_filter = request.GET.get('category', '')

    respondents = Respondent.objects.all()

    # search
    if q:
        respondents = respondents.filter(
            Q(name__icontains=q)      |
            Q(email__icontains=q)     |
            Q(unique_id__icontains=q) |
            Q(city__icontains=q)      |
            Q(phone__icontains=q)
        )

    # filters
    if city_filter:
        respondents = respondents.filter(city=city_filter)
    if category_filter:
        respondents = respondents.filter(category=category_filter)

    # pagination
    paginator = Paginator(respondents, 25)
    page      = request.GET.get('page', 1)
    page_obj  = paginator.get_page(page)

    # metrics
    total      = Respondent.objects.count()
    active     = Respondent.objects.filter(status='active').count()
    cooloff    = Respondent.objects.filter(status='cooloff').count()
    inactive   = Respondent.objects.filter(status='inactive').count()
    leads      = ReferralStatus.objects.filter(stage='lead').count()
    fits       = ReferralStatus.objects.filter(stage='fit').count()
    completions = ReferralStatus.objects.filter(stage='completion').count()

    # city breakdown
    city_counts = Respondent.objects.values('city').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    # referrals
    referrals = ReferralStatus.objects.select_related(
        'referrer', 'referred', 'survey'
    ).order_by('-created_at')[:20]

    cities     = Respondent.objects.values_list(
        'city', flat=True
    ).distinct()
    categories = Respondent.objects.values_list(
        'category', flat=True
    ).distinct()

    return render(request, 'panel/dashboard.html', {
        'page_obj':        page_obj,
        'q':               q,
        'city_filter':     city_filter,
        'category_filter': category_filter,
        'cities':          cities,
        'categories':      categories,
        'total':           total,
        'active':          active,
        'cooloff':         cooloff,
        'inactive':        inactive,
        'leads':           leads,
        'fits':            fits,
        'completions':     completions,
        'city_counts':     city_counts,
        'referrals':       referrals,
    })

@staff_member_required
def update_stage(request, pk):
    """
    Staff updates referral stage:
    lead → fit → completion
    """
    referral   = get_object_or_404(ReferralStatus, pk=pk)
    new_stage  = request.POST.get('stage')
    valid      = ['lead', 'fit', 'completion']

    if request.method == 'POST' and new_stage in valid:
        referral.stage = new_stage
        if new_stage == 'completion':
            referral.is_paid = True
        referral.save()
        messages.success(
            request,
            f'Stage updated to {new_stage} for '
            f'{referral.referred.name}.'
        )
    return redirect('dashboard')

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