from django.shortcuts import render, redirect, reverse
# from .email_backend import EmailBackend
from django.contrib import messages

from .forms import CustomUserForm
from .models import CustomUser
from voting.forms import VoterForm
from django.contrib.auth import login, logout, authenticate
from voting.models import Votes, Results, CandidateResults, Position
# Create your views here.
from django.urls import reverse_lazy
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse, HttpResponse


def account_login(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("adminDashboard"))
        else:
            return redirect(reverse("voterDashboard"))

    context = {}
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get(
            'email'), password=request.POST.get('password'))
        if user != None:
            if user.user_type!='1' and user.voter.otp_entered >= 5:
                messages.error(request, "You are blocked because of multiple failed otp attempts. Please contact admin.")
                return redirect("/")

            login(request, user)
            
            if user.user_type == '1':
                return redirect(reverse("adminDashboard"))
            else:
                user.voter.otp_sent = 0
                user.voter.save()
                return redirect(reverse("voterDashboard"))
        else:              
            messages.error(request, "Invalid details")
            return redirect("/")

    return render(request, "voting/login.html", context)


def account_register(request):
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {
        'form1': userForm,
        'form2': voterForm
    }
    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "Account created. You can login now!")
            return redirect(reverse('account_login'))
        else:
            messages.error(request, "Provided data failed validation")
            # return account_login(request)
    return render(request, "voting/reg.html", context)


def account_logout(request):
    user = request.user
    if user.is_authenticated:
        if user.user_type != '1':
            voter = request.user.voter
            voter.verified = False
            voter.save()
        logout(request)
        messages.success(request, "Thank you for visiting us!")
    else:
        messages.error(
            request, "You need to be logged in to perform this action")

    return redirect(reverse("account_login"))

def view_bulletin(request):
    votes = Votes.objects.all()
    context = {
        'votes': votes,
        'page_title': 'Bulletin board'
    }
    return render(request, "voting/bulletin.html", context)

def view_results(request):
    pos = []
    cand = []
    positions = []
   
    for r in Results.objects.all():
        if request.user.user_type!='1' and request.user.voter.branch != r.allowed_branches:
            continue
        pos.append(r.position_name)
        
        stat = []
        win_vote = 0
        for c in r.candidate_result.all():
            win_vote=max(win_vote, c.vote_count)
        for c in r.candidate_result.all():
            if c.vote_count == win_vote:
                stat.append(True)
            else:
                stat.append(False)
        
        cand.append(zip(r.candidate_result.all(),stat))
        if not Position.objects.filter(id = r.posid):
            positions.append('Error')
        else:
            positions.append(Position.objects.filter(id = r.posid)[0])

   
    counter = [i for i in range(len(pos))]
    context = {
        
        'results': zip(pos, positions, counter, cand),
        'page_title': 'Results',
        
    }
    return render(request, "results.html", context)

def forget_password(request):
    return render(request, "password_reset.html", {})

def send_mail(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        u = CustomUser.objects.get(email = email)
        if u is None or u.user_type=='1':
            messages.error(request, 'No voter account is being registered with the provided email address.')
            return redirect(reverse("account_login"))
        otp = generate_otp()
        u.otp_reset_pass = otp
        u.save()
        msg = "Dear " + str(u) + ", kindly use " + \
                    str(otp) + " as your OTP for password reset"
        message_is_sent = send_email(email, msg)
        if message_is_sent:
            messages.success(request,"OTP has been sent to your email. Please provide it in the box provided below")
        else:
            messages.error(request,"OTP not sent. Please try again")
            return redirect(reverse('forget_password'))
        return render(request, "otp_verification.html", {})

def otp_verify(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        newPass = request.POST.get('newPass')
        print(newPass)
        u = CustomUser.objects.get(email = email)
        if u is None or u.user_type=='1' or otp !=u.otp_reset_pass :
            messages.error(request, 'Invalid otp')
            return redirect(reverse("account_login"))
        u.password = make_password(newPass)
        u.save()
        messages.success(request, "PASSWORD successfully changed!!")
    return redirect(reverse("account_login"))

def send_email(email, msg):
    """Read More
    https://www.multitexter.com/developers
    """
    from django.core.mail import send_mail
    if email is None  is None:
        raise Exception("Email cannot be Null")
    try:
        i = send_mail(
                        'OTP for logging in EVoting System',
                        msg,
                        'evoting.iitr@gmail.com',
                        [email],
                        fail_silently=False,
                    )
        if i == 1:
            return True
        else:
            return False
    except:
        return False
   
def generate_otp():
    """Link to this function
    https://www.codespeedy.com/otp-generation-using-random-module-in-python/
    """
    import random as r
    otp = ""
    for i in range(r.randint(5, 8)):
        otp += str(r.randint(1, 9))
    return otp