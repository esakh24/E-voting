from django.db import models
from account.models import CustomUser
from multiselectfield import MultiSelectField
from administrator.models import adminKeys
from django.utils import timezone
from datetime import datetime, date, time
import json
# Create your models here.


class Dicty(models.Model):
    name      = models.CharField(max_length=70)
    def __str__(self):
        return self.name
class KeyVal(models.Model):
    # container = models.ForeignKey(Dicty,on_delete=models.CASCADE, db_index=True)
    dkey       = models.CharField(db_index=True, max_length=200)
    dvalue     = models.IntegerField(db_index=True, default=-1)
    # def __str__(self):
    #     return (self.key, self.value)

class SharesKeyVal(models.Model):
    # container = models.ForeignKey(Dicty,on_delete=models.CASCADE, db_index=True)
    dkey       = models.EmailField()
    dvalue     = models.TextField(db_index=True, max_length=12000, default="")
    def set_dvalue(self,x):
        self.dvalue = json.dumps(x)
    
    def get_dvalue(self):
        if self.dvalue is "":
            return []
        return json.loads(self.dvalue)

class Voter(models.Model):
    class Branch(models.IntegerChoices):
        AR = 1,"Arch"
        CS = 2, "CSE"
        BT = 3, "Biotech"
        EE = 4, "Electrical"
        ECE = 5, "Electronics"
    # BRANCH = ((1,"Architectural"), (2,"biomedical"), (3,"civil"), (4,"mechanical"), (5,"electrical"), (6,"aerospace"), (7,"CS"), (8,"chemical"))
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11, unique=True)  # Used for OTP
    branch = models.IntegerField(default=Branch.AR, choices=Branch.choices, verbose_name="branch")
    otp = models.CharField(max_length=20, null=True)
    verified = models.BooleanField(default=False)
    voted = models.CharField(default="", max_length= 10000)
    otp_sent = models.IntegerField(default=0)  # Control how many OTPs are sent
    otp_sent_time = models.TimeField(default=time(11, 34, 56))
    otp_entered = models.IntegerField(default=0)
    
    

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name
    
    def set_voted(self,x):
        
        voted_list = self.get_voted()
        voted_list.append(x)
        self.voted = json.dumps(voted_list)
    
    def get_voted(self):
        if self.voted is "":
            return []
        return json.loads(self.voted)

# class Branch_(models.Model):
#     branch_id = models.IntegerField(default=1)
#     branch_name = models.CharField(max_length=30)
class Branches(models.Model):
    bid = models.IntegerField(default=1)
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name

class Position(models.Model):
    class Branch(models.IntegerChoices):
        AR = 1,"Arch"
        CS = 2, "CSE"
        BT = 3, "Biotech"
        EE = 4, "Electrical"
        ECE = 5, "Electronics"
    name = models.CharField(max_length=50, unique=True)
    max_vote = models.IntegerField()
    voter_count = models.IntegerField(default=5)
    candidate_count = models.IntegerField(default=2)
    priority = models.IntegerField()
    # Create election
    candidate_dict = models.ManyToManyField(KeyVal)
    candidate_filled = models.IntegerField(default=0)
    # BRANCH = ((1,"arch"), (2,"cse"), (3,"biotech"), (4,""))#TODO: multiple branches
    is_tallied = models.BooleanField(default=False )
    allowed_branches = models.IntegerField(default=Branch.AR, choices=Branch.choices, verbose_name="branch")
    admin_keys = models.ForeignKey(adminKeys,  on_delete=models.CASCADE, null=True, blank=True)
    shares_collected = models.ManyToManyField(SharesKeyVal)
    init_time = models.TimeField(default=time(11, 34, 56))
    end_time = models.TimeField(default=time(11, 34, 56))
    init_date = models.DateField( default=date(2022, 12, 25))
    end_date = models.DateField( default=date(2022, 12, 25))
    enc_msg1 = models.CharField(default="0",max_length=520)
    enc_msg2 = models.CharField(default="0",max_length=520) 

    def __str__(self):
        return self.name


class Candidate(models.Model):
    fullname = models.CharField(max_length=50, unique=True)
    photo = models.ImageField(upload_to="candidates")
    bio = models.TextField()
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    def __str__(self):
        return self.fullname


class Votes(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    enc_vote = models.CharField(max_length=10000000, default="")

class CandidateResults(models.Model):
    fullname = models.CharField(max_length=50)
    photo = models.ImageField(upload_to="candidates")
    position = models.CharField(max_length=255)
    vote_count = models.IntegerField(default=0)
    

class Results(models.Model):
    class Branch(models.IntegerChoices):
        AR = 1,"Arch"
        CS = 2, "CSE"
        BT = 3, "Biotech"
        EE = 4, "Electrical"
        ECE = 5, "Electronics"
    # BRANCH = ((1,"arch"), (2,"cse"), (3,"biotech"))
    allowed_branches = models.IntegerField(default=Branch.AR, choices=Branch.choices, verbose_name="branch")
    position_name = models.CharField(max_length=255)
    posid = models.IntegerField(default=0)
    candidate_result = models.ManyToManyField(CandidateResults)