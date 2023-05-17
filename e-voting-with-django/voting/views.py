from django.shortcuts import render, redirect, reverse
from account.views import account_login
from .models import Position, Candidate, Voter, Votes
from administrator.utils import encrypt_votes
from django.http import JsonResponse
from django.utils.text import slugify
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from datetime import date, time, datetime
import django
import requests
import json
from helios_lib.models import HeliosElection, HeliosVoter
# Create your views here.


def index(request):
    if not request.user.is_authenticated:
        return account_login(request)
    context = {}
    # return render(request, "voting/login.html", context)


def generate_ballot( *args, display_controls=False):
    branch_id = args[0]
    positions = Position.objects.order_by('priority').all()
    output = ""
    candidates_data = ""
    num = 1
    # return None
    positions = Position.objects.filter(allowed_branches = branch_id)
    instruction = 'No candidates enrolled yet...'
    for position in positions:
       
        if position.end_date<date.today() or(position.end_date==date.today() and position.end_time<time(datetime.now().hour, datetime.now().minute, datetime.now().second)):
            continue
        name = position.name
        # position_name = slugify(name)
        position_name = name
        candidates = Candidate.objects.filter(position=position)
        for candidate in candidates:
            if position.max_vote > 1:
                instruction = "You may select up to " + \
                    str(position.max_vote) + " candidates"
                input_box = '<input type="checkbox" value="'+str(candidate.id)+'" class="flat-red ' + \
                    position_name+'" name="' + \
                    position_name+"[]" + '">'
            else:
                instruction = "Select only one candidate"
                input_box = '<input value="'+str(candidate.id)+'" type="radio" class="flat-red ' + \
                    position_name+'" name="'+position_name+'">'
            image = "/media/" + str(candidate.photo)
            candidates_data = candidates_data + '<li>' + input_box + '<button type="button" class="btn btn-primary btn-sm btn-flat clist platform" data-fullname="'+candidate.fullname+'" data-bio="'+candidate.bio+'"><i class="fa fa-search"></i> Platform</button><img src="' + \
                image+'" height="100px" width="100px" class="clist"><span class="cname clist">' + \
                candidate.fullname+'</span></li>'
        up = ''
        if position.priority == 1:
            up = 'disabled'
        down = ''
        if position.priority == positions.count():
            down = 'disabled'
        output = output + f"""<div class="row">	<div class="col-xs-12"><div class="box box-solid" id="{position.id}">
             <div class="box-header with-border">
            <h3 class="box-title"><b>{name}</b></h3>"""

        if display_controls:
            output = output + f""" <div class="pull-right box-tools">
        <button type="button" class="btn btn-default btn-sm moveup" data-id="{position.id}" {up}><i class="fa fa-arrow-up"></i> </button>
        <button type="button" class="btn btn-default btn-sm movedown" data-id="{position.id}" {down}><i class="fa fa-arrow-down"></i></button>
        </div>"""

        output = output + f"""</div>
        <div class="box-body">
        <p>{instruction}
        <span class="pull-right">
        
        <button type="button" class="btn btn-success btn-sm btn-flat reset" data-desc="{position_name}"><i class="fa fa-refresh"></i> Reset</button>
        </span>
        </p>
        <div id="candidate_list">
        <ul>
        {candidates_data}
        </ul>
        </div>
        </div>
        </div>
        </div>
        </div>
        """
        position.priority = num
        position.save()
        num = num + 1
        candidates_data = ''
    print(output)
    return output


def fetch_ballot(request):
    output = generate_ballot(request.user.voter.branch, display_controls=True)
    return JsonResponse(output, safe=False)


def generate_otp():
    """Link to this function
    https://www.codespeedy.com/otp-generation-using-random-module-in-python/
    """
    import random as r
    otp = ""
    for i in range(r.randint(5, 8)):
        otp += str(r.randint(1, 9))
    return otp


def dashboard(request):
    user = request.user
    # * Check if this voter has been verified
    if user.voter.otp is None or user.voter.verified == False:
        if not settings.SEND_OTP:
            # Bypassuser.voter.verified
            msg = bypass_otp()
            messages.success(request, msg)
            return redirect(reverse('show_ballot'))
        else:
            return redirect(reverse('voterVerify'))
    else:
        return redirect(reverse('show_ballot'))


def verify(request):
    context = {
        'page_title': 'OTP Verification'
    }
    return render(request, "voting/voter/verify.html", context)


def resend_otp(request):
    """API For SMS
    I used https://www.multitexter.com/ API to send SMS
    You might not want to use this or this service might not be available in your Country
    For quick and easy access, Toggle the SEND_OTP from True to False in settings.py
    """
    user = request.user
    voter = user.voter
    error = False
    if settings.SEND_OTP:
        if voter.otp_sent >= 5:
            error = True
            response = "You have requested OTP five times. You cannot do this again! Please enter previously sent OTP"
        else:
            phone = user.email
            # Now, check if an OTP has been generated previously for this voter
            otp = voter.otp
            # Generate new OTP
            otp = generate_otp()
            voter.otp = otp
            voter.save()
            try:
                msg = "Dear " + str(user) + ", kindly use " + \
                    str(otp) + " as your OTP"
                message_is_sent = send_email(phone, msg)
                if message_is_sent:  # * OTP was sent successfully
                    # Update how many OTP has been sent to this voter
                    # Limited to Three so voters don't exhaust OTP balance
                    voter.otp_sent = voter.otp_sent + 1
                    voter.otp_sent_time = time(datetime.now().hour, datetime.now().minute, datetime.now().second)
                    voter.save()

                    response = "OTP has been sent to your email. Please provide it in the box provided below"
                else:
                    error = True
                    response = "OTP not sent. Please try again"
            except Exception as e:
                response = "OTP could not be sent." + str(e)

                # * Send OTP
    else:
        #! Update all Voters record and set OTP to 0000
        #! Bypass OTP verification by updating verified to 1
        #! Redirect voters to ballot page
        response = bypass_otp()
    return JsonResponse({"data": response, "error": error})


def bypass_otp():
    Voter.objects.all().filter(otp=None, verified=False).update(otp="0000", verified=True)
    response = "Kindly cast your vote"
    return response

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
   


def verify_otp(request):
    error = True
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    else:
        otp = request.POST.get('otp')
        voter = request.user.voter
        voter.otp_entered+=1
        voter.save()
        if(voter.otp_entered>5):
            messages.error(request,"Multiple failed OTPs led to account block. Please contact admin.")
            return redirect(reverse('account_logout'))
        if otp is None:
            messages.error(request, "Please provide valid OTP")
        else:
            # Get User OTP
            voter = request.user.voter
            if not (datetime.now().hour - voter.otp_sent_time.hour ==0 and  datetime.now().minute - voter.otp_sent_time.minute ==0 and  datetime.now().second - voter.otp_sent_time.second <= 30):
                messages.error(request, "Your OTP session has expired. Kindly click on resend for new OTP.")
            else:
                db_otp = voter.otp
                if db_otp != otp:
                    messages.error(request, "Provided OTP is not valid")
                else:
                    voter.verified = True
                    voter.otp_sent = 0
                    voter.otp_entered = 0
                    voter.save()
                    print(voter.verified, voter.otp)
                    error = False
                    messages.success(
                        request, "You are now verified. Please cast your vote")
                    
                
    if error:
        return redirect(reverse('voterVerify'))
    return redirect(reverse('show_ballot'))


def show_ballot(request):
    print(request.user.voter.get_voted)
    
    positions = Position.objects.filter(allowed_branches = request.user.voter.branch)
    new_positions = []
    new_candidates = []
    voteleft = False
    for position in positions:
        if position.id not in request.user.voter.get_voted():
            if position.end_date<date.today() or(position.end_date==date.today() and position.end_time<time(datetime.now().hour, datetime.now().minute, datetime.now().second)):
                continue
            elif position.init_date>date.today() or(position.init_date==date.today() and position.init_time>time(datetime.now().hour, datetime.now().minute, datetime.now().second)):
                continue
            else:
                voteleft = True
                new_positions.append(position)
                new_candidates.append(Candidate.objects.filter(position=position))

    if not voteleft:    
        context = {
                'my_votes': Votes.objects.filter(voter=request.user.voter),
            }
        return render(request, "voting/voter/result.html", context)
        
    context = {
        'zip_position_cand': zip(new_positions, new_candidates),
    }
    print(new_candidates, new_positions)
    return render(request, "voting/voter/ballot.html", context)


def preview_vote(request):
    if request.method != 'POST':
        error = True
        response = "Please browse the system properly"
    else:
        output = ""
        form = dict(request.POST)
        # We don't need to loop over CSRF token
        form.pop('csrfmiddlewaretoken', None)
        error = False
        data = []
        positions = Position.objects.all()
        for position in positions:
            max_vote = position.max_vote
            # pos = slugify(position.name)
            pos_id = position.id
            
            this_key = position.name
            print(this_key)
            form_position = form.get(this_key)
            print(form_position)
            print(form)
            if form_position is None:
                continue
            # Max Vote == 1
            try:
                form_position = form_position[0]
                candidate = Candidate.objects.get(
                    position=position, id=form_position)
                enc_vote, k1 = auditVote(position, candidate)
                output = f"""
                        <div class='row votelist' style='padding-bottom: 2px'>
                            <div class='col-sm-4'><h3 style="color:green"><b>{position.name}</b></h3></div>
                                <hr>
                                <table id="example1" class="table table-bordered">
    <thead>
        <th>El Gamal Variables</th>
        <th>Values</th>
        
    </thead>
    <tbody>

    
<tr>
    <td>Encrypted Vote</td>

    <td style="display: flex;">

    <div id ="enc_vote" style="overflow: hidden; text-overflow: ellipsis;width: 200px;display: inline;
    white-space: nowrap;border: 1px solid gray; padding: 3px;">
    {enc_vote}
    </div><button id="copyButton" onclick="copy('enc_vote')" style="display: inline; float: right; margin: 2px 2px; margin-left: 6px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clipboard-fill" viewBox="0 0 16 16">
    <path fill-rule="evenodd" d="M10 1.5a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-1Zm-5 0A1.5 1.5 0 0 1 6.5 0h3A1.5 1.5 0 0 1 11 1.5v1A1.5 1.5 0 0 1 9.5 4h-3A1.5 1.5 0 0 1 5 2.5v-1Zm-2 0h1v1A2.5 2.5 0 0 0 6.5 5h3A2.5 2.5 0 0 0 12 2.5v-1h1a2 2 0 0 1 2 2V14a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V3.5a2 2 0 0 1 2-2Z"/>
    </svg></button> 
    </td>
</tr>
<tr>
    <td>Prime number p</td>

    <td style="display: flex;">

    <div id ="prime" style="overflow: hidden; text-overflow: ellipsis;width: 200px;display: inline;
    white-space: nowrap;border: 1px solid gray; padding: 3px;">
    {position.admin_keys.p}
    </div><button id="copyButton" onclick="copy('prime')" style="display: inline; float: right; margin: 2px 2px; margin-left: 6px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clipboard-fill" viewBox="0 0 16 16">
    <path fill-rule="evenodd" d="M10 1.5a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-1Zm-5 0A1.5 1.5 0 0 1 6.5 0h3A1.5 1.5 0 0 1 11 1.5v1A1.5 1.5 0 0 1 9.5 4h-3A1.5 1.5 0 0 1 5 2.5v-1Zm-2 0h1v1A2.5 2.5 0 0 0 6.5 5h3A2.5 2.5 0 0 0 12 2.5v-1h1a2 2 0 0 1 2 2V14a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V3.5a2 2 0 0 1 2-2Z"/>
    </svg></button> 
    </td>
</tr>
<tr>
    <td>Random number</td>

    <td style="display: flex;">

    <div id ="random" style="overflow: hidden; text-overflow: ellipsis;width: 200px;display: inline;
    white-space: nowrap;border: 1px solid gray; padding: 3px;">
    {k1}
    </div><button id="copyButton" onclick="copy('random')" style="display: inline; float: right; margin: 2px 2px; margin-left: 6px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clipboard-fill" viewBox="0 0 16 16">
    <path fill-rule="evenodd" d="M10 1.5a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-1Zm-5 0A1.5 1.5 0 0 1 6.5 0h3A1.5 1.5 0 0 1 11 1.5v1A1.5 1.5 0 0 1 9.5 4h-3A1.5 1.5 0 0 1 5 2.5v-1Zm-2 0h1v1A2.5 2.5 0 0 0 6.5 5h3A2.5 2.5 0 0 0 12 2.5v-1h1a2 2 0 0 1 2 2V14a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V3.5a2 2 0 0 1 2-2Z"/>
    </svg></button> 
    </td>
</tr>
<tr>
    <td>Generator</td>

    <td style="display: flex;">

    <div id ="generator" style="overflow: hidden; text-overflow: ellipsis;width: 200px;display: inline;
    white-space: nowrap;border: 1px solid gray; padding: 3px;">
    {position.admin_keys.g}
    </div><button id="copyButton" onclick="copy('generator')" style="display: inline; float: right; margin: 2px 2px; margin-left: 6px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clipboard-fill" viewBox="0 0 16 16">
    <path fill-rule="evenodd" d="M10 1.5a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-1Zm-5 0A1.5 1.5 0 0 1 6.5 0h3A1.5 1.5 0 0 1 11 1.5v1A1.5 1.5 0 0 1 9.5 4h-3A1.5 1.5 0 0 1 5 2.5v-1Zm-2 0h1v1A2.5 2.5 0 0 0 6.5 5h3A2.5 2.5 0 0 0 12 2.5v-1h1a2 2 0 0 1 2 2V14a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V3.5a2 2 0 0 1 2-2Z"/>
    </svg></button> 
    </td>
</tr>

<tr>
    <td>Y = generator^private_key</td>

    <td style="display: flex;">

    <div id ="y" style="overflow: hidden; text-overflow: ellipsis;width: 200px;display: inline;
    white-space: nowrap;border: 1px solid gray; padding: 3px;">
    {position.admin_keys.Y}
    </div><button id="copyButton" onclick="copy('y')" style="display: inline; float: right; margin: 2px 2px; margin-left: 6px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clipboard-fill" viewBox="0 0 16 16">
    <path fill-rule="evenodd" d="M10 1.5a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-1Zm-5 0A1.5 1.5 0 0 1 6.5 0h3A1.5 1.5 0 0 1 11 1.5v1A1.5 1.5 0 0 1 9.5 4h-3A1.5 1.5 0 0 1 5 2.5v-1Zm-2 0h1v1A2.5 2.5 0 0 0 6.5 5h3A2.5 2.5 0 0 0 12 2.5v-1h1a2 2 0 0 1 2 2V14a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V3.5a2 2 0 0 1 2-2Z"/>
    </svg></button> 
    </td>
</tr>
</tbody>
</table>
<textarea id="download_txt" hidden>Encrypted Vote: {enc_vote} &#13;&#10;Prime number p: {position.admin_keys.p}
&#13;&#10;Random number: {k1}&#13;&#10;Generator: {position.admin_keys.g}&#13;&#10;Y = generator^private_key: {position.admin_keys.Y}</textarea>
</div><hr/>
                """
                print(output)
            except Exception as e:
                error = True
                response = "Please, browse the system properly"
    context = {
        'error': error,
        'list': output
    }
    print(output)
    return JsonResponse(context, safe=False)

def search_candidateID(pos_obj, name):
    for val in pos_obj.candidate_dict.all():
        if val.dkey == name:
            return val.dvalue
    return -1

def auditVote(pos, candidate):
    
    try:
        # vote = Votes.objects.get(id=request.POST.get('voteid'))
        
        vote_array = [0]*pos.candidate_count
        vote_array[search_candidateID(pos, candidate.fullname)] = 1
        enc_vote, k1 = encrypt_votes(vote= vote_array, p=int(pos.admin_keys.p), g=int(pos.admin_keys.g), Y=int(pos.admin_keys.Y),audit_vote = True)
        return enc_vote, k1
        # messages.success(request, "Successfully audited")
        context = {
                'my_votes': Votes.objects.filter(voter=request.user.voter),
            }
        return render(request, "voting/voter/result.html", context)
    except Exception as e:
        # messages.error(request, "Please, browse the system properly " + str(e))
        
        return -1
    
    
    
def submit_ballot(request):
    if request.method != 'POST':
        print(request.method, "oooooooooooooooooooooooooooo")
        messages.error(request, "Please, browse the system properly")
        return redirect(reverse('show_ballot'))

    print(request.user.voter.otp, request.user.voter.verified )

    # Verify if the voter has voted or not
    voter = request.user.voter
    # if voter.voted:
    #     messages.error(request, "You have voted already")
    #     return redirect(reverse('voterDashboard'))

    form = dict(request.POST)
    form.pop('csrfmiddlewaretoken', None)  # Pop CSRF Token
    form.pop('submit_vote', None)  # Pop Submit Button

    # Ensure at least one vote is selected
    if len(form.keys()) < 1:
        messages.error(request, "Please select at least one candidate")
        return redirect(reverse('show_ballot'))
    positions = Position.objects.filter(allowed_branches = request.user.voter.branch)
    form_count = 0
    naivePos = -1
    for position in positions:
        # pos = slugify(position.name)
        pos = position.name
        pos_id = position.id
        
        this_key = pos
        form_position = form.get(this_key)
        if form_position is None:
            continue
        if position.end_date<date.today() or(position.end_date==date.today() and position.end_time<time(datetime.now().hour, datetime.now().minute, datetime.now().second)):
            messages.error(request, 'Ooops voting period ended for position: '+ position.name)
            continue
        naivePos = pos_id  

        # Max Vote == 1
        form_count += 1
        try:
            form_position = form_position[0]
            candidate = Candidate.objects.get(
                position=position, id=form_position)
            vote = Votes()
            vote.candidate = candidate
            vote.voter = voter
            vote.position = position
            pos = Position.objects.get(pk = pos_id)
            vote_array = [0]*pos.candidate_count
            vote_array[search_candidateID(pos, candidate.fullname)] = 1
            enc_vote, k1 = encrypt_votes(vote=vote_array, p=int(pos.admin_keys.p), g=int(pos.admin_keys.g), Y=int(pos.admin_keys.Y), audit_vote =True)
            vote.enc_vote = str(enc_vote)
            prod = 1
            if not position.enc_msg1 == "0":
                prod = int(position.enc_msg1)
            position.enc_msg1 =str((prod*pow(int(position.admin_keys.g),k1,int(position.admin_keys.p)))%int(position.admin_keys.p))
            prod = 1
            if not position.enc_msg2 == "0":
                prod = int(position.enc_msg2)
            position.enc_msg2 =str((prod*pow(int(position.admin_keys.Y),k1,int(position.admin_keys.p)))%int(position.admin_keys.p))
            position.save()
            vote.save()
        except Exception as e:
            print(e)
            messages.error(
                request, "Please, browse the system properly " + str(e))
            return redirect(reverse('show_ballot'))
    # Count total number of records inserted
    # Check it viz-a-viz form_count
    # inserted_votes = Votes.objects.filter(voter=voter)
    # if (inserted_votes.count() != form_count):
    #     # Delete
    #     inserted_votes.delete()
    #     messages.error(request, "Please try voting again!")
    #     return redirect(reverse('show_ballot'))
    # else:
        # Update Voter profile to voted
    if naivePos == -1:
        messages.error(request, "Form not submitted!!!")
    else:
        voter.set_voted(naivePos)
        voter.save()
    messages.success(request, "Thanks for voting")
    print(request.user.voter.otp, request.user.voter.verified )
    return redirect(reverse('voterDashboard'))

def view_bulletin(request):
    votes = Votes.objects.all()
    context = {
        'votes': votes,
        'page_title': 'Bulletin board'
    }
    return render(request, "voting/bulletin.html", context)