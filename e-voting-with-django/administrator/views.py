from django.shortcuts import render, reverse, redirect
from voting.models import Voter, Position, Candidate, Votes, KeyVal
from .models import adminKeys
from . import utils, shamir_secret_sharing
from account.models import CustomUser, StrKeyVal
from account.forms import CustomUserForm
from voting.forms import *
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import json  # Not used
from django_renderpdf.views import PDFView
from helios_lib.models import HeliosElection, HeliosVoter
from helios_lib.config import ELGAMAL_PARAMS

import shamirs


def find_n_winners(data, n):
    """Read More
    https://www.geeksforgeeks.org/python-program-to-find-n-largest-elements-from-a-list/
    """
    final_list = []
    candidate_data = data[:]
    # print("Candidate = ", str(candidate_data))
    for i in range(0, n):
        max1 = 0
        if len(candidate_data) == 0:
            continue
        this_winner = max(candidate_data, key=lambda x: x['votes'])
        # TODO: Check if None
        this = this_winner['name'] + \
            " with " + str(this_winner['votes']) + " votes"
        final_list.append(this)
        candidate_data.remove(this_winner)
    return ", &nbsp;".join(final_list)


class PrintView(PDFView):
    template_name = 'admin/print.html'
    prompt_download = True

    @property
    def download_name(self):
        return "result.pdf"

    def get_context_data(self, *args, **kwargs):
        title = "E-voting"
        try:
            file = open(settings.ELECTION_TITLE_PATH, 'r')
            title = file.read()
        except:
            pass
        context = super().get_context_data(*args, **kwargs)
        position_data = {}
        for position in Position.objects.all():
            candidate_data = []
            winner = ""
            for candidate in Candidate.objects.filter(position=position):
                this_candidate_data = {}
                votes = Votes.objects.filter(candidate=candidate).count()
                this_candidate_data['name'] = candidate.fullname
                this_candidate_data['votes'] = votes
                candidate_data.append(this_candidate_data)
            print("Candidate Data For  ", str(
                position.name), " = ", str(candidate_data))
            # ! Check Winner
            if len(candidate_data) < 1:
                winner = "Position does not have candidates"
            else:
                # Check if max_vote is more than 1
                if position.max_vote > 1:
                    winner = find_n_winners(candidate_data, position.max_vote)
                else:

                    winner = max(candidate_data, key=lambda x: x['votes'])
                    if winner['votes'] == 0:
                        winner = "No one voted for this yet position, yet."
                    else:
                        """
                        https://stackoverflow.com/questions/18940540/how-can-i-count-the-occurrences-of-an-item-in-a-list-of-dictionaries
                        """
                        count = sum(1 for d in candidate_data if d.get(
                            'votes') == winner['votes'])
                        if count > 1:
                            winner = f"There are {count} candidates with {winner['votes']} votes"
                        else:
                            winner = "Winner : " + winner['name']
            print("Candidate Data For  ", str(
                position.name), " = ", str(candidate_data))
            position_data[position.name] = {
                'candidate_data': candidate_data, 'winner': winner, 'max_vote': position.max_vote}
        context['positions'] = position_data
        print(context)
        return context


def dashboard(request):
 
    candidates = Candidate.objects.all()
    voters = Voter.objects.all()
    voted_voters = Voter.objects.filter(voted=1)
    list_of_candidates = []
    votes_count = []
    chart_data = {}
    positions = []
    for r in Results.objects.all():
        list_of_candidates = []
        votes_count = []
        positions.append(r.position_name)
        for c in r.candidate_result.all():
            list_of_candidates.append(c.fullname)
            votes_count.append(c.vote_count)
        chart_data[r] = {
            'candidates': list_of_candidates,
            'votes': votes_count,
            'pos_id': r.id
        }
    
    context = {
        'position_count': Position.objects.all().count(),
        'candidate_count': candidates.count(),
        'voters_count': voters.count(),
        'voted_voters_count': voted_voters.count(),
        'positions': positions,
        'chart_data': chart_data,
        'page_title': "Dashboard",
        'zip_res_pos':zip(Results.objects.all(), positions)
    }
    
    return render(request, "admin/home.html", context)


def voters(request):
    voters = Voter.objects.all()
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {
        'form1': userForm,
        'form2': voterForm,
        'voters': voters,
        'page_title': 'Voters List'
    }
    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "New voter created")
        else:
            messages.error(request, "Form validation failed")
    
    branches = []
    for v in Voter.objects.all():
        branches.append(Position.Branch.choices[v.branch-1][1])
    context['voters'] = zip(Voter.objects.all(), branches)
    return render(request, "admin/voters.html", context)


def view_voter_by_id(request):
    voter_id = request.GET.get('id', None)
    voter = Voter.objects.filter(id=voter_id)
    context = {}
    if not voter.exists():
        context['code'] = 404
    else:
        context['code'] = 200
        voter = voter[0]
        context['first_name'] = voter.admin.first_name
        context['last_name'] = voter.admin.last_name
        context['phone'] = voter.phone
        context['id'] = voter.id
        context['email'] = voter.admin.email
        context['branch'] = voter.branch
    return JsonResponse(context)


def view_position_by_id(request):
    pos_id = request.GET.get('id', None)
    pos = Position.objects.filter(id=pos_id)
    context = {}
    if not pos.exists():
        context['code'] = 404
    else:
        context['code'] = 200
        pos = pos[0]
        context['name'] = pos.name
        context['max_vote'] = pos.max_vote
        context['id'] = pos.id
        context['candidate_count'] = pos.candidate_count
        context['voter_count'] = pos.voter_count
        context['branch'] = pos.allowed_branches
        context['init_date'] = pos.init_date
        context['end_date'] = pos.end_date
        context['init_time'] = pos.init_time
        context['end_time'] = pos.end_time
        
    return JsonResponse(context)


def updateVoter(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        instance = Voter.objects.get(id=request.POST.get('id'))
        user = CustomUserForm(request.POST or None, instance=instance.admin)
        voter = VoterForm(request.POST or None, instance=instance)
        user.save()
        voter.save()
        messages.success(request, "Voter's bio updated")
    except Exception as e: 
        print(e)
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('adminViewVoters'))


def deleteVoter(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        admin = Voter.objects.get(id=request.POST.get('id')).admin
        admin.delete()
        messages.success(request, "Voter Has Been Deleted")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('adminViewVoters'))


def viewPositions(request):
    positions = Position.objects.all()
    form = PositionForm(request.POST or None)
    context = {
        'positions': positions,
        'form1': form,
        'page_title': "Positions",
        
        
    }
    
    if request.method == 'POST':
        if form.is_valid():
            form = form.save(commit=False)
            form.priority = positions.count() + 1  # Just in case it is empty.
            
            # # Create election
            p1,g1,Y1,x1= utils.generate_keys()
            n = len(CustomUser.objects.filter(user_type = 1))
            raw_shares = shamirs.shares(x1, quantity=n, modulus=p1, threshold=n)
            shares=[[a.index, a.value] for a in raw_shares]
            print(shares,"......................")
            for u, share in zip(CustomUser.objects.filter(user_type = 1), shares):
                pos_key_dict = u.pos_key_dict
                strkeyvalobj = StrKeyVal(dkey=form.name)
                strkeyvalobj.set_dvalue(share)
                strkeyvalobj.save()
                pos_key_dict.add(strkeyvalobj)
                u.save()
            keys = adminKeys(p = str(p1), g =str(g1), Y=str(Y1), x=str(x1))
            keys.save()
            form.admin_keys = keys
            form.save()
                        
            messages.success(request, "New Position Created")
        else:
            messages.error(request, "Form errors")
    
    positions = Position.objects.all()
    disable_action = []
    tally_disable=[]
    branches=[]
    for position in positions:
        branches.append(Position.Branch.choices[position.allowed_branches-1][1])
        if position.end_date<date.today() or(position.end_date==date.today() and position.end_time<time(datetime.now().hour, datetime.now().minute, datetime.now().second)):
            tally_disable.append(False)
        else:
            tally_disable.append(True) #True
        if position.init_date<date.today() or(position.init_date==date.today() and position.init_time<time(datetime.now().hour, datetime.now().minute, datetime.now().second)):
            disable_action.append(True) #true
        else:
            disable_action.append(False)
    
    zip_pos_act = zip(positions, disable_action, tally_disable, branches)
    context.update({'zip_pos_act':zip_pos_act})
    return render(request, "admin/positions.html", context)


def updatePosition(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        position = Position.objects.get(id=request.POST.get('id'))
        old_name = position.name
        if position.init_date<date.today() or(position.init_date==date.today() and position.init_time<time(datetime.now().hour, datetime.now().minute, datetime.now().second)):
            messages.error(request, "You can't update position information after election started!")
            return redirect(reverse('viewPositions'))
        instance = Position.objects.get(id=request.POST.get('id'))
        pos = PositionForm(request.POST or None, instance=instance)
        pos.save()
        position = Position.objects.get(id=request.POST.get('id'))
        for adminu in CustomUser.objects.filter(user_type = 1):
            key_val_obj = search_keyVal_admin(adminu, old_name)
            if key_val_obj !=-1:
                print(old_name, "OOOOOOOOOLDDDDDDDDDDD")
                pos_key_dict = adminu.pos_key_dict
                strkeyvalobj = StrKeyVal(dkey=position.name)
                strkeyvalobj.set_dvalue(key_val_obj.get_dvalue())
                print(position.name, "NEWWWWWWWWWWWWWWWWWWWWWW")
                print(strkeyvalobj.get_dvalue())
                strkeyvalobj.save()
                pos_key_dict.add(strkeyvalobj)
                
                adminu.save()
                adminu.pos_key_dict.remove(key_val_obj)
                key_val_obj.delete()
                adminu.save()
        messages.success(request, "Position has been updated")
    except Exception as E:
        print(E)
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewPositions'))

def get_candidate_list(pos):
    cand = [None]*pos.candidate_filled
    print(pos)
    for p in pos.candidate_dict.all():
        try:
            cand[p.dvalue] = Candidate.objects.get(fullname = p.dkey)
            print("??????????????????",cand[p.dvalue])
        except Exception as E:
            print("********************",p.dkey)
            print("********************************",E)

    return cand

def tallyPosition(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")

    try:
        pos_id = request.POST.get('posid')
        pos = Position.objects.get(id=request.POST.get('posid'))
        position = pos
        context = {}
        context['name'] =pos.name
        context['page_title'] = 'Results for ' + pos.name
        
        admin_emails = [us.email for us in CustomUser.objects.filter(user_type = 1)]
        
        if not (position.end_date<date.today() or(position.end_date==date.today() and position.end_time<time(datetime.now().hour, datetime.now().minute, datetime.now().second))):
            messages.error(request, "You can't tally votes in between the election or before it begins.")
            return redirect(reverse('viewPositions'))
        if len(position.shares_collected.all()) < len(CustomUser.objects.filter(user_type = 1)):
            for keyvalobj in position.shares_collected.all():
                if keyvalobj.dkey == request.user.email:
                    for ee in position.shares_collected.all():
                        admin_emails.remove(ee.dkey)
                    context['admins'] = admin_emails
                    return render(request, "voting/tallyresults.html", context)
            strkeyvalobj = SharesKeyVal(dkey=request.user.email)
            for keyvalobj in request.user.pos_key_dict.all():
                if keyvalobj.dkey == position.name:
                    strkeyvalobj.set_dvalue(keyvalobj.get_dvalue())
                    break
            strkeyvalobj.save()
            position.shares_collected.add(strkeyvalobj)
            position.save()
            if len(position.shares_collected.all()) < len(CustomUser.objects.filter(user_type = 1)):
                for ee in position.shares_collected.all():
                        admin_emails.remove(ee.dkey)
                context['admins'] = admin_emails
                return render(request, "voting/tallyresults.html", context)
        
        raw_shamir_shares = [keyvalobj.get_dvalue() for keyvalobj in position.shares_collected.all()]
        # x = shamir_secret_sharing.reconstruct_secret(shamir_shares, int(pos.admin_keys.p))
        shamir_shares = [shamirs.share(a[0], a[1], int(pos.admin_keys.p)) for a in raw_shamir_shares]
        x = shamirs.interpolate(shamir_shares, threshold=len(CustomUser.objects.filter(user_type = 1)))
        print(x)
        print(pos.admin_keys.x)
        print(pos.admin_keys.p)
        print(x == int(pos.admin_keys.x), '<<<<<<<<<<<<<<<<<<<<<<<<<<<')
        votes = Votes.objects.filter(position = pos).values()
        enc_add = utils.encrypt_votes([0]*pos.candidate_count, int(pos.admin_keys.p), int(pos.admin_keys.g), int(pos.admin_keys.Y))
        for v in votes:
            enc_vote_num = utils.str_to_list(v.get('enc_vote')) 
            enc_add=utils.add_encrypted_votes(int(pos.admin_keys.p), enc_add, enc_vote_num)
        dec_add = utils.decrypt_vote(enc_add, x, int(pos.admin_keys.p), int(pos.admin_keys.g))
        
        messages.success(request, "Votes calculated successfully")
    except Exception as E:
        print(E)
        messages.error(request, "Access To This Resource Denied")
   
    cand_list = get_candidate_list(pos)
    if position.is_tallied == False:
        res = Results(position_name = position.name, allowed_branches = position.allowed_branches, posid = position.id)
        for candid, dec_v in zip(cand_list, dec_add):
            cand_obj= CandidateResults(fullname = candid.fullname, photo= candid.photo, position=candid.position.name, vote_count=dec_v)
            cand_obj.save()
            res.save()
            res.candidate_result.add(cand_obj)
        position.is_tallied = True
        position.save()

    context['candidates'] = cand_list
    context['results'] = dec_add
    context['candres'] = zip(context['candidates'], dec_add)
    return render(request, "voting/tallyresults.html", context)
    

def deletePosition(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        position = Position.objects.get(id=request.POST.get('id'))
        if position.init_date<date.today() or(position.init_date==date.today() and position.init_time<time(datetime.now().hour, datetime.now().minute, datetime.now().second)):
            if position.end_date>date.today() or (position.end_date==date.today() and position.end_time>time(datetime.now().hour, datetime.now().minute, datetime.now().second)):
                messages.error(request, "You can't delete position information after election started!")
                return redirect(reverse('viewPositions'))
        pos = Position.objects.get(id=request.POST.get('id'))
        for adminu in CustomUser.objects.filter(user_type = 1):
            key_val_obj = search_keyVal_admin(adminu, position.name)
            if key_val_obj !=-1:
                adminu.pos_key_dict.remove(key_val_obj)
                key_val_obj.delete()
                adminu.save()

        for c in pos.candidate_dict.all():
            c.delete()
        for s in pos.shares_collected.all():
            s.delete()
        # pos.candidate_dict.clear()
        # pos.shares_collected.clear()
        pos.delete()
        messages.success(request, "Position Has Been Deleted")
    except Exception as E:
        print(E)
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewPositions'))

def assign_candidate_id(pos_obj):
    i = set()
    for keyvalobj in pos_obj.candidate_dict.all():
        i.add(keyvalobj.dvalue)
    cnt = 0
    for elm in i:
        if(elm!=cnt):
            return cnt
        cnt+=1
    return cnt
def search_keyVal(pos_obj, name):
    for keyvalueobj in pos_obj.candidate_dict.all():
        
        if keyvalueobj.dkey == name:
            
            return keyvalueobj
    return -1

def search_keyVal_admin(admin_obj, name):
    for keyvalueobj in admin_obj.pos_key_dict.all():
        
        if keyvalueobj.dkey == name:
            
            return keyvalueobj
    return -1

def viewCandidates(request):
    # a = CandidateResults.objects.filter(position = 'general_secretory-arch')
    # for vv in a:
    #     vv.delete()
    # a = Results.objects.filter(position_name = 'general_secretory-arch')
    # for vv in a:
    #     vv.delete()
    
    candidates = Candidate.objects.all()
    form = CandidateForm(request.POST or None, request.FILES or None)
    context = {
        'candidates': candidates,
        'form1': form,
        'page_title': 'Candidates'
    }
    
    if request.method == 'POST':
        if form.is_valid():
            pos = form['position'].value()
            pos_obj = Position.objects.get(pk=pos)
            if(pos_obj.candidate_filled>=Position.objects.get(pk=pos).candidate_count):
                messages.error(request,"NUMBER OF REGISTERED CANDIDATES EXCEEDED")
            else:
                
                candidate_dict = pos_obj.candidate_dict
                keyvalobj = KeyVal(dkey=form['fullname'].value(), dvalue = assign_candidate_id(pos_obj))
                keyvalobj.save()
                candidate_dict.add(keyvalobj)
           
                pos_obj.candidate_filled+=1
                pos_obj.save()
               
                form = form.save()
            messages.success(request, "New Candidate Created")
        else:
            messages.error(request, "Form errors")

    return render(request, "admin/candidates.html", context)


def updateCandidate(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    
    try:
        candidate_id = request.POST.get('id')
        candidate = Candidate.objects.get(id=candidate_id)
        old_name =candidate.fullname
        prev_pos_id = candidate.position.id
        form = CandidateForm(request.POST or None,
                             request.FILES or None, instance=candidate)
        
        if form.is_valid():
            new_pos_id = int(form['position'].value())
            new_name = form['fullname'].value()
            
            print(new_name ,old_name)
            if(prev_pos_id!= new_pos_id or new_name != old_name):
                new_pos_obj = Position.objects.get(pk=new_pos_id)
                prev_pos_obj = Position.objects.get(pk=prev_pos_id)
                print(new_pos_obj, prev_pos_obj)
                print(new_pos_id, prev_pos_id)
                if (new_pos_obj.candidate_filled<=new_pos_obj.candidate_count):
                    new_pos_obj.candidate_filled+=1
                    new_pos_obj.save()
                    prev_pos_obj.candidate_filled-=1
                    key_val_obj = search_keyVal(prev_pos_obj, old_name)
                    print(key_val_obj, ">>>>>>>>>>>>>>>>>>>>>>>>>>")
                    prev_pos_obj.candidate_dict.remove(key_val_obj)
                    key_val_obj.delete()
                    prev_pos_obj.save()
                    candidate_dict = new_pos_obj.candidate_dict
                    keyvalobj = KeyVal(dkey=form['fullname'].value(), dvalue = assign_candidate_id(new_pos_obj))
                    keyvalobj.save()
                    candidate_dict.add(keyvalobj)
                else:
                    messages.error(request, "candidate number exceeded")
                    return redirect(reverse('viewCandidates'))
             
            form.save()
            messages.success(request, "Candidate Data Updated")
                
        else:
            messages.error(request, "Form has errors")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewCandidates'))


def deleteCandidate(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        candidate_id = request.POST.get('id')
        candidate = Candidate.objects.get(id=candidate_id)
        prev_pos_id = candidate.position.pk
        prev_pos_obj = Position.objects.get(pk=prev_pos_id)
        prev_pos_obj.candidate_filled-=1
        key_val_obj = search_keyVal(prev_pos_obj, candidate.fullname)
        prev_pos_obj.candidate_dict.remove(key_val_obj)
        key_val_obj.delete()
        prev_pos_obj.save()
        pos = Candidate.objects.get(id=request.POST.get('id'))
        pos.delete()
        messages.success(request, "Candidate Has Been Deleted")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewCandidates'))


def view_candidate_by_id(request):
    candidate_id = request.GET.get('id', None)
    candidate = Candidate.objects.filter(id=candidate_id)
    context = {}
    if not candidate.exists():
        context['code'] = 404
    else:
        candidate = candidate[0]
        context['code'] = 200
        context['fullname'] = candidate.fullname
        previous = CandidateForm(instance=candidate)
        context['form'] = str(previous.as_p())
    return JsonResponse(context)


def ballot_position(request):
    context = {
        'page_title': "Ballot Position"
    }
    return render(request, "admin/ballot_position.html", context)


def update_ballot_position(request, position_id, up_or_down):
    try:
        context = {
            'error': False
        }
        position = Position.objects.get(id=position_id)
        if up_or_down == 'up':
            priority = position.priority - 1
            if priority == 0:
                context['error'] = True
                output = "This position is already at the top"
            else:
                Position.objects.filter(priority=priority).update(
                    priority=(priority+1))
                position.priority = priority
                position.save()
                output = "Moved Up"
        else:
            priority = position.priority + 1
            if priority > Position.objects.all().count():
                output = "This position is already at the bottom"
                context['error'] = True
            else:
                Position.objects.filter(priority=priority).update(
                    priority=(priority-1))
                position.priority = priority
                position.save()
                output = "Moved Down"
        context['message'] = output
    except Exception as e:
        context['message'] = e

    return JsonResponse(context)

def unblock_user(request):
    voter_id = request.GET.get('id', None)
    voters = Voter.objects.filter(id=voter_id)
    for voter in voters:
        voter.otp_entered = 0
        voter.save()
    return JsonResponse({})

def ballot_title(request):
    from urllib.parse import urlparse
    url = urlparse(request.META['HTTP_REFERER']).path
    from django.urls import resolve
    try:
        redirect_url = resolve(url)
        title = request.POST.get('title', 'No Name')
        file = open(settings.ELECTION_TITLE_PATH, 'w')
        file.write(title)
        file.close()
        messages.success(
            request, "Election title has been changed to " + str(title))
        return redirect(url)
    except Exception as e:
        messages.error(request, e)
        return redirect("/")


def viewVotes(request):
    votes = Votes.objects.all()
    context = {
        'votes': votes,
        'page_title': 'Votes'
    }
    return render(request, "admin/votes.html", context)


def resetVote(request):
    Votes.objects.all().delete()
    Voter.objects.all().update(voted="")
    messages.success(request, "All votes has been reset")
    return redirect(reverse('viewVotes'))

