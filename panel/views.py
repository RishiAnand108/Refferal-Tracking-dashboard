# panel/views.py
import csv
import json
import openpyxl

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count

from .models import Respondent, Survey, ReferralStatus
from .forms import SignupForm, AddRespondentForm
from .utils import get_referrer_from_session


# ── Home ──────────────────────────────────────────────────
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('staff-login')


# ── Staff Login ───────────────────────────────────────────
def staff_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user     = authenticate(request, username=username,
                                password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request,
                'Invalid credentials or not a staff member.')

    return render(request, 'panel/login.html', {})


# ── Staff Logout ──────────────────────────────────────────
def staff_logout(request):
    logout(request)
    return redirect('staff-login')


# ── Referral link tracking ────────────────────────────────
def track_referral(request, referral_code):
    try:
        referrer = Respondent.objects.get(referral_code=referral_code)
        request.session['referral_code'] = str(referral_code)
        request.session['referrer_name'] = referrer.name
        messages.info(request,
            f'You were referred by {referrer.name}. '
            f'Complete signup to help them earn a bonus!')
    except Respondent.DoesNotExist:
        messages.warning(request, 'Invalid referral link.')
    return redirect('signup')


# ── Signup with referral attribution ─────────────────────
def signup_view(request):
    referrer      = get_referrer_from_session(request)
    referrer_name = request.session.get('referrer_name', '')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            respondent = form.save(commit=False)
            if referrer:
                respondent.referred_by = referrer
            respondent.save()

            if referrer:
                ReferralStatus.objects.create(
                    referrer     = referrer,
                    referred     = respondent,
                    stage        = 'lead',
                    bonus_amount = 50.00
                )

            respondent.set_cooloff()
            request.session.pop('referral_code', None)
            request.session.pop('referrer_name', None)

            messages.success(request,
                f'Welcome {respondent.name}! '
                f'Your unique ID is {respondent.unique_id}.')
            return redirect('staff-login')
    else:
        form = SignupForm()

    return render(request, 'panel/signup.html', {
        'form':          form,
        'referrer_name': referrer_name,
    })


# ── Staff dashboard ───────────────────────────────────────
@login_required(login_url='/login/')
def dashboard(request):
    q               = request.GET.get('q', '')
    city_filter     = request.GET.get('city', '')
    category_filter = request.GET.get('category', '')

    respondents = Respondent.objects.all()

    if q:
        respondents = respondents.filter(
            Q(name__icontains=q)      |
            Q(email__icontains=q)     |
            Q(unique_id__icontains=q) |
            Q(city__icontains=q)      |
            Q(phone__icontains=q)
        )
    if city_filter:
        respondents = respondents.filter(city=city_filter)
    if category_filter:
        respondents = respondents.filter(category=category_filter)

    paginator = Paginator(respondents, 25)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    total       = Respondent.objects.count()
    active      = Respondent.objects.filter(status='active').count()
    cooloff     = Respondent.objects.filter(status='cooloff').count()
    inactive    = Respondent.objects.filter(status='inactive').count()
    leads       = ReferralStatus.objects.filter(stage='lead').count()
    fits        = ReferralStatus.objects.filter(stage='fit').count()
    completions = ReferralStatus.objects.filter(
                    stage='completion').count()

    city_counts = Respondent.objects.values('city').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    referrals  = ReferralStatus.objects.select_related(
        'referrer', 'referred', 'survey'
    ).order_by('-created_at')[:20]

    cities     = Respondent.objects.values_list(
                    'city', flat=True).distinct()
    categories = Respondent.objects.values_list(
                    'category', flat=True).distinct()

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


# ── Update referral stage ─────────────────────────────────
@login_required(login_url='/login/')
def update_stage(request, pk):
    referral  = get_object_or_404(ReferralStatus, pk=pk)
    new_stage = request.POST.get('stage')
    valid     = ['lead', 'fit', 'completion']

    if request.method == 'POST' and new_stage in valid:
        referral.stage = new_stage
        if new_stage == 'completion':
            referral.is_paid = True
        referral.save()
        messages.success(request,
            f'Stage updated to {new_stage} for '
            f'{referral.referred.name}.')
    return redirect('dashboard')


# ── Add respondent manually ───────────────────────────────
@login_required(login_url='/login/')
def add_respondent(request):
    if request.method == 'POST':
        form = AddRespondentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,
                'Respondent added successfully.')
            return redirect('dashboard')
    else:
        form = AddRespondentForm()
    return render(request, 'panel/add_respondent.html',
                  {'form': form})


# ── Export CSV / Excel ────────────────────────────────────
@login_required(login_url='/login/')
def export_data(request):
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
            content_type='application/vnd.openxmlformats-'
                         'officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = \
            'attachment; filename=respondents.xlsx'
        wb.save(response)
        return response

    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename=respondents.csv'
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


# ── AI categorization ─────────────────────────────────────
def ai_categorize(request):
    if request.method == 'POST':
        notes = request.POST.get('notes', '').lower()

        keywords = {
            'Healthcare': ['hospital', 'doctor', 'nurse',
                          'medical', 'clinic', 'health',
                          'pharma', 'patient', 'icu', 'ward'],
            'Finance':    ['bank', 'finance', 'insurance',
                          'investment', 'stock', 'loan',
                          'mutual fund', 'ca', 'accountant'],
            'Retail':     ['shop', 'store', 'mall', 'retail',
                          'sales', 'ecommerce', 'amazon',
                          'flipkart', 'merchant'],
            'FMCG':       ['fmcg', 'consumer', 'grocery',
                          'food', 'beverage', 'brand',
                          'hul', 'nestle', 'itc'],
            'Technology': ['tech', 'software', 'developer',
                          'engineer', 'it', 'startup',
                          'coding', 'programmer', 'data'],
        }

        scores = {
            cat: sum(1 for w in words if w in notes)
            for cat, words in keywords.items()
        }

        best       = max(scores, key=scores.get)
        best_score = scores[best]

        if best_score == 0:
            best, confidence = 'Other', 'low'
        elif best_score == 1:
            confidence = 'medium'
        else:
            confidence = 'high'

        return JsonResponse({
            'category':   best,
            'confidence': confidence,
            'reason':     f'Notes contain keywords associated '
                          f'with {best} sector.',
            'stub_note':  'Connect Claude API for production use.'
        })

    return JsonResponse({'error': 'POST required'}, status=400)