import os
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render
from paypal.standard.forms import PayPalPaymentsForm
from bridge.forms import ExpertForm, StudentForm, AddLectureForm
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from bridge.models import Expert, AddLecture, Student, Expert_Following, Expert_Student_Block, Student_block_count, \
    StudentLectureAttended, CommonNews, CommonExpertNews, ExpertOnlineStatus, NewsFeed, ExpertReview, StudentReview, \
    LectureHistory, E2E, ExpertEnq, AdminNews

hasher = PBKDF2PasswordHasher()


def payment_process(request):
    host = request.get_host()
    paypal_dict = {
    'business': settings.PAYPAL_RECEIVER_EMAIL ,
    'amount': "10",
    'item_name': 'Item_Name_xyz',
    'invoice': "Test Payment Invoice",
    'currency_code': 'USD',
    'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
    'return_url': 'http://{}{}'.format(host, reverse('payment_done')),
    'cancel_return': 'http://{}{}'.format(host, reverse('payment_canceled')) }
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'payment_process.html', {'form': form })

def visitor(request):
    u = User.objects.all()
    context = dict()
    context['user'] = u
    expert_m = Expert.objects.filter(Department='management')
    expert_e = Expert.objects.filter(Department='engineering')
    expert_p = Expert.objects.filter(Department='pharamacy')
    context['expert_e'] = expert_e
    context['expert_m'] = expert_m
    context['expert_p'] = expert_p
    context['news'] = NewsFeed.objects.all()
    return render(request, 'visitor.html', context)


def expert_exists(email):
    try:
        expert_exist = Expert.objects.get(Personal_Email=email)
        return expert_exist
    except Exception as e:
        return None


def student_exists(email):
    try:
        student_exist = Student.objects.get(Personal_Email=email)
        return student_exist
    except Exception as e:
        return None


def register_expert(request):
    try:
        # if this is a POST request we need to process the form data
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = ExpertForm(request.POST)
            # check whether it's valid:
            try:
                exist_expert = expert_exists(request.user.email)
            except:
                exist_expert = expert_exists(request.POST['Personal_Email'])
            first_name = get_first_name(request.POST['name'])
            last_name = get_last_name(request.POST['name'])
            if exist_expert:
                Expert.objects.filter(Personal_Email=request.user.email).update(name=request.POST['name'],
                                            Designation=request.POST['Designation'],
                                            Company_Name=request.POST['Company_Name'],
                                            Department=request.POST['Department'],
                                            Skill=request.POST['Skill'],
                                            Field_of_Experience=request.POST['Field_of_Experience'],
                                            mobile=request.POST['mobile'],
                                            about=request.POST['about'],
                                            )

                MyProfileForm = ExpertForm(request.POST, request.FILES)
                profile = Expert.objects.get(Personal_Email=request.user.email)
                try:
                    if request.FILES['Profile_piture']:
                        profile.Profile_piture = request.FILES['Profile_piture']
                except:
                    pass
                try:
                    if request.FILES['Icard_Picture']:
                        profile.Icard_Picture = request.FILES['Icard_Picture']
                except:
                    pass
                profile.save()

                u = User.objects.filter(email=request.user.email).update(first_name=first_name, last_login=datetime.today(),
                                        last_name=last_name,
                                       )
                context = dict()
                user = check_auth(request)

                if user is not None:
                    if user.is_active:
                        login(request, user)
                expert_login = Expert.objects.get(Personal_Email=request.user.email)
                context['each_expert'] = expert_login
                context['expert'] = expert_login
                try:
                    expert_online = ExpertOnlineStatus.objects.get(expert_id=expert_login.id).is_online
                except:
                    expert_online = False
                context['online'] = expert_online
                return render(request, 'edit_expert_profile.html', context)

            else:
                if form.is_valid():
                    form.save()
                    MyProfileForm = ExpertForm(request.POST, request.FILES)
                    profile = Expert.objects.get(Personal_Email=request.POST['Personal_Email'])
                    profile.Profile_piture = request.FILES['Profile_piture']
                    profile.Icard_Picture = request.FILES['Icard_Picture']
                    profile.save()

                    u = User.objects.create(password=hasher.encode(password=request.POST['password'],
                                                                   salt='salt',
                                                                   iterations=50000), is_active=0, is_staff=0,
                                            is_superuser=0, first_name=first_name, last_login=datetime.today(),
                                            last_name=last_name, email=request.POST['Personal_Email'],
                                            username=generate_username(first_name, last_name), date_joined=datetime.today())
                    messages.success(request, first_name + " "+ last_name+ ' has been registered successfully! As soon as  you will be verified by Admin, you can logged in with your Email and password.')
                    form = ExpertForm()

                    return render(request, 'expert_register_ex.html', {'form': form})
        else:
            form = ExpertForm()

            return render(request, 'expert_register_ex.html', {'form': form})
        # if a GET (or any other method) we'll create a blank form

    except Exception as e:
        return HttpResponseRedirect('/visitor/')


def get_first_name(fullname):
    firstname = ''
    try:
        firstname = fullname.split()[0]
    except Exception as e:
        return None
    return firstname


def get_last_name(fullname):
    lastname = ''
    try:
        index=0
        for part in fullname.split():
            if index > 0:
                if index > 1:
                    lastname += ' '
                lastname +=  part
            index += 1
    except Exception as e:
            return None
    return lastname


def generate_username(first_name,last_name):
    val = "{0}{1}".format(first_name[0],last_name).lower()
    x=0
    while True:
        if x == 0 and User.objects.filter(username=val).count() == 0:
            return val
        else:
            new_val = "{0}{1}".format(val,x)
            if User.objects.filter(username=new_val).count() == 0:
                return new_val
        x += 1
        if x > 1000000:
            raise Exception("Name is super popular!")


def student_registration(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = StudentForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            form.save()
            first_name = get_first_name(request.POST['name'])
            last_name = get_last_name(request.POST['name'])
            u = User.objects.create(password=hasher.encode(password=request.POST['password'],
                                  salt='salt',
                                  iterations=50000), is_active=1, is_staff=0, is_superuser=0, first_name=first_name, last_login=datetime.today(),
                                last_name=last_name, email=request.POST['Personal_Email'], username=generate_username(first_name,last_name), date_joined=datetime.today())
            MyProfileForm = StudentForm(request.POST, request.FILES)
            profile = Student.objects.get(Personal_Email=request.POST['Personal_Email'])
            profile.Profile_piture = request.FILES['Profile_piture']
            profile.save()
            messages.success(request, "You have successfully registered! Please login with valid credentials.")
            return HttpResponseRedirect('/student_registration/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = StudentForm()

    return render(request, 'student_registration.html', {'form': form})


def check_login(request):
    try:
        try:
            uname = request.POST['username']
            pwd = request.POST['password']
        except:
            uname = request.user.username
            pwd = request.user.password
        user = authenticate(username=uname, password=pwd)
        if user is None:
            User = get_user_model()
            user_queryset = User.objects.all().filter(email__iexact=uname)
            if user_queryset:
                username = user_queryset[0].username
                user = authenticate(username=username, password=pwd)
        if user is None:
            usr = User.objects.filter(username=uname)
            user = usr.get(password=pwd)
        login(request, user)
        if user.is_superuser == True:
            return HttpResponseRedirect('/user_admin/')
        ex = check_expert_login(user.email)
        if ex:
            return HttpResponseRedirect('/expert_index/')
        st = check_student_login(user.email)
        if st:
            return HttpResponseRedirect('/student_index/')

    except Exception as e:
        return HttpResponseRedirect('/visitor/')


def check_expert_login(email):
    try:
        expert_login = Expert.objects.get(Personal_Email=email)
    except:
        expert_login = None
    return expert_login


def check_student_login(email):
    try:
        student_login = Student.objects.get(Personal_Email=email)
    except:
        student_login = None
    return student_login

def check_auth(req):
    try:
        uname = req.POST['username']
        pwd = req.POST['password']
        # password=hasher.encode(password=req.POST['password'],
        # salt='salt',
        # iterations=50000)
    except:
        uname = req.user.username
        pwd = req.user.password
    try:
        user = authenticate(username=uname, password=pwd)
        if user is None:
            User = get_user_model()
            user_queryset = User.objects.all().filter(email__iexact=uname)
            if user_queryset:
                username = user_queryset[0].username
                user = authenticate(username=username, password=pwd)
        if user is None:
            usr = User.objects.filter(username=uname)
            user = usr.get(password=pwd)
    except Exception as e:
        usr = User.objects.filter(username=uname)
        user = usr.get(password=pwd)

    return user


def followers(request):
    user = check_auth(request)

    if user is not None:
        if user.is_active:
            login(request, user)
            context = dict()
            expert_login = check_expert_login(request.user.email)
            if expert_login:
                context['expert'] = expert_login
                student = Student.objects.all()
                student_list_follower = []
                student_list_following = []
                expert_connection_list = []
                expert_req_connection_list = []

                for st in student:
                    is_ex_follower = Expert_Following.objects.filter(Student_id_id=st.id).filter(Expert_id_id=expert_login.id).filter(Is_follow=1).filter(Is_follow_accepted=1)
                    is_ex_following = Expert_Following.objects.filter(Student_id_id=st.id).filter(Expert_id_id=expert_login.id).filter(Is_follow=1).filter(Is_follow_accepted=0)
                    if is_ex_following:
                        student_list_following.append(st)
                    if is_ex_follower:
                        student_list_follower.append(st)
                connection_request = E2E.objects.filter(expert_get=expert_login.id).filter(is_connect_request=1).filter(is_connect=0)
                for each_cn in connection_request:
                    expert_req_connection = Expert.objects.get(id=each_cn.expert_sent.id)
                    expert_req_connection_list.append(expert_req_connection)
                context['expert_req_connection_list'] = expert_req_connection_list

                connections = E2E.objects.filter(expert_get=expert_login.id).filter(is_connect=1)
                if connections:
                    for each_cn in connections:
                        expert_connection = Expert.objects.get(id=each_cn.expert_sent.id)
                        expert_connection_list.append(expert_connection)
                else:
                    connections = E2E.objects.filter(expert_sent_id=expert_login.id).filter(is_connect=1)
                    for each_cn in connections:
                        expert_connection = Expert.objects.get(id=each_cn.expert_get)
                        expert_connection_list.append(expert_connection)

                context['expert_connection_list'] = expert_connection_list
                context['student_list_following'] = student_list_following
                context['student_list_follower'] = student_list_follower
                try:
                    expert_online = ExpertOnlineStatus.objects.get(expert_id=expert_login.id).is_online
                except:
                    expert_online = False
                context['online'] = expert_online
                return render(request, 'followers.html', context)
            else:
                return HttpResponseRedirect(reverse('visitor'))
        else:
            return HttpResponseRedirect(reverse('visitor'))
    else:
        return HttpResponseRedirect(reverse('visitor'))


def update_followers(request, id=''):
    user = check_auth(request)
    if user is not None:
        if user.is_active:
            login(request, user)
            context = dict()
            expert_login = check_expert_login(request.user.email)
            if expert_login:
                context['expert'] = expert_login
                is_ex_follower = Expert_Following.objects.filter(Student_id_id=id).filter(Expert_id_id=expert_login.id).update(Is_follow_accepted=1)
                msg = expert_login.name +" has accpeted your request."
                CommonNews.objects.create(news=msg, student_id=id)
                return HttpResponseRedirect('/followers/')
            else:
                return HttpResponseRedirect(reverse('visitor'))
        else:
            return HttpResponseRedirect(reverse('visitor'))
    else:
        return HttpResponseRedirect(reverse('visitor'))


def remove_followers(request, id=''):
    user = check_auth(request)
    if user is not None:
        if user.is_active:
            login(request, user)
            context = dict()
            expert_login = check_expert_login(request.user.email)
            if expert_login:
                context['expert'] = expert_login
                is_ex_follower = Expert_Following.objects.filter(Student_id_id=id).filter(Expert_id_id=expert_login.id)
                is_ex_follower.delete()
                return HttpResponseRedirect('/followers/')
            else:
                return HttpResponseRedirect(reverse('visitor'))
        else:
            return HttpResponseRedirect(reverse('visitor'))
    else:
        return HttpResponseRedirect(reverse('visitor'))


def accept_connection_req(request, expert_req_id='', expert_login_id=''):
    user = check_auth(request)
    if user is not None:
        if user.is_active:
            login(request, user)
            context = dict()
            expert_login = check_expert_login(request.user.email)
            if expert_login:
                context['expert'] = expert_login
                try:
                    is_ex_follower = E2E.objects.filter(expert_get=expert_login.id).filter(expert_sent_id=expert_req_id)
                except:
                    is_ex_follower = E2E.objects.filter(expert_sent_id=expert_login.id).filter(expert_get=expert_req_id)

                if is_ex_follower:
                    is_ex_follower.update(is_connect=1)
                return HttpResponseRedirect('/followers/')
            else:
                return HttpResponseRedirect(reverse('visitor'))
        else:
            return HttpResponseRedirect(reverse('visitor'))
    else:
        return HttpResponseRedirect(reverse('visitor'))

def remove_connection(request, expert_req_id='', expert_login_id=''):
    user = check_auth(request)
    if user is not None:
        if user.is_active:
            login(request, user)
            context = dict()
            expert_login = check_expert_login(request.user.email)
            if expert_login:
                context['expert'] = expert_login
                try:
                    is_ex_follower = E2E.objects.filter(expert_get=expert_login.id).filter(expert_sent_id=expert_req_id)
                except:
                    is_ex_follower = E2E.objects.filter(expert_sent_id=expert_login.id).filter(expert_get=expert_req_id)

                is_ex_follower.delete()
                return HttpResponseRedirect('/followers/')
            else:
                return HttpResponseRedirect(reverse('visitor'))
        else:
            return HttpResponseRedirect(reverse('visitor'))
    else:
        return HttpResponseRedirect(reverse('visitor'))

def block_follower(request, id=''):
    user = check_auth(request)
    if user is not None:
        if user.is_active:
            login(request, user)
            context = dict()
            expert_login = check_expert_login(request.user.email)
            if expert_login:
                context['expert'] = expert_login
                is_ex_follower = Expert_Student_Block.objects.filter(Student_id_id=id).filter(Expert_id_id=expert_login.id)
                if is_ex_follower:
                    is_ex_follower.update(is_block=1)
                else:
                    Expert_Student_Block.objects.create(Student_id_id=id, Expert_id_id=expert_login.id, is_block=1)
                is_ex_follower = Expert_Following.objects.filter(Student_id_id=id).filter(
                    Expert_id_id=expert_login.id)
                try:
                    is_block = Student_block_count.objects.get(Student_id_id=id)
                    block_count = int(is_block.block_count)
                    if block_count < 5:
                        block_count_new = block_count + 1
                        Student_block_count.objects.filter(Student_id_id=id).update(block_count=block_count_new)
                        if is_ex_follower:
                            is_ex_follower.update(Is_follow=0, Is_follow_accepted=0)
                    else:
                        if is_ex_follower:
                            is_ex_follower.delete()
                except:
                    is_block = Student_block_count.objects.create(Student_id_id=id,block_count=1)
                return HttpResponseRedirect('/followers/')
            else:
                return HttpResponseRedirect(reverse('visitor'))
        else:
            return HttpResponseRedirect(reverse('visitor'))
    else:
        return HttpResponseRedirect(reverse('visitor'))

def get_video_delivered(expert):
    lecture_delivered_dict = dict()
    for each_expert in expert:
        lecture_delivered = LectureHistory.objects.filter(expert_id_id=each_expert.id).count()
        lecture_delivered_dict[each_expert.id] = lecture_delivered
    return lecture_delivered_dict

def get_followers_count(expert):
    lecture_delivered_dict = dict()
    for each_expert in expert:
        lecture_delivered = Expert_Following.objects.filter(Expert_id_id=each_expert.id).filter(Is_follow=1).filter(Is_follow_accepted=1)
        lecture_delivered_dict[each_expert.id] = lecture_delivered.count()
    return lecture_delivered_dict

def get_expert_review(expert):
    rating_dict = dict()
    for each_expert in expert:
        lecture_delivered = ExpertReview.objects.filter(expert_id=each_expert.id)
        rating_dict[each_expert.id] = lecture_delivered.count()
    return rating_dict

def get_connect_status(expert_id,expert_m):
    is_connected = 'connect'
    for each_expert in expert_m:
        try:
            try:
                is_exists =E2E.objects.filter(expert_sent=expert_id).get(expert_get=each_expert.id)
            except:
                is_exists = E2E.objects.filter(expert_sent=each_expert.id).get(expert_get=expert_id)
            if is_exists:
                is_connect = is_exists.is_connect_request
                if is_connect:
                    if is_exists.is_connect:
                        is_connected = 'connected'
                    else:
                        is_connected = 'requested'
                else:
                    is_connected = 'connect'
            else:
                is_connected = 'connect'
        except Exception as e:
            is_connected = 'connect'
    rating_dict = dict()
    for each_expert in expert_m:
        rating_dict[each_expert.id] = is_connected
    return rating_dict


def send_connect_request(request, expert_req_id='', expert_login_id=''):
    try:
        E = E2E.objects.update_or_create(expert_get=int(expert_req_id), expert_sent_id=expert_login_id,is_connect_request=1, is_connect=0)
        expert = Expert.objects.get(id=expert_login_id)
        msg = "Expert "+ expert.name +" wants to connect with you."
        CommonExpertNews.objects.create(news=msg, expert_id=expert_req_id,is_available=0)
        return HttpResponse(E)
    except Exception as e:
        return None

def expert_index(request):
    try:
        user = check_auth(request)
        if user is not None:
            if user.is_active:
                login(request, user)
                context = dict()
                expert_login = check_expert_login(request.user.email)
                if expert_login:
                    m_lecture_delivered, p_lecture_delivered, e_lecture_delivered, o_lecture_delivered = 0, 0, 0, 0
                    p_follower_count, m_follower_count, e_follower_count, o_follower_count = 0, 0, 0, 0
                    p_reviews, e_reviews, m_reviews, o_reviews = 0,0,0,0
                    m_connect, p_connect, o_connect, e_connect = 0, 0, 0, 0
                    context['expert'] = expert_login
                    expert_m = Expert.objects.filter(Department='management').exclude(id=expert_login.id)
                    expert_e = Expert.objects.filter(Department='enginering').exclude(id=expert_login.id)
                    expert_p = Expert.objects.filter(Department='pharamacy').exclude(id=expert_login.id)
                    expert_o = Expert.objects.filter(Department='other').exclude(id=expert_login.id)
                    if expert_m:
                        m_lecture_delivered = get_video_delivered(expert_m)
                        m_follower_count = get_followers_count(expert_m)
                        m_reviews = get_expert_review(expert_m)
                        m_connect = get_connect_status(expert_login.id,expert_m)
                    context['m_connect'] = m_connect
                    context['m_reviews'] = m_reviews
                    context['m_follower_count'] = m_follower_count
                    context['m_lecture_delivered'] = m_lecture_delivered
                    if expert_e:
                        e_lecture_delivered = get_video_delivered(expert_e)
                        e_follower_count = get_followers_count(expert_e)
                        e_reviews = get_expert_review(expert_e)
                        e_connect = get_connect_status(expert_login.id,expert_e)
                    context['e_connect'] = e_connect

                    context['e_reviews'] = e_reviews
                    context['e_follower_count'] = e_follower_count
                    context['e_lecture_delivered'] = e_lecture_delivered
                    if expert_p:
                        p_lecture_delivered = get_video_delivered(expert_p)
                        p_follower_count = get_followers_count(expert_p)
                        p_reviews = get_expert_review(expert_p)
                        p_connect = get_connect_status(expert_login.id,expert_p)
                    context['p_connect'] = p_connect

                    context['p_reviews'] = p_reviews
                    context['p_follower_count'] = p_follower_count
                    context['p_lecture_delivered'] = p_lecture_delivered
                    if expert_o:
                        o_lecture_delivered = get_video_delivered(expert_o)
                        o_follower_count = get_followers_count(expert_o)
                        o_reviews = get_expert_review(expert_o)
                        o_connect = get_connect_status(expert_login.id,expert_o)
                    context['o_connect'] = o_connect
                    context['o_reviews'] = o_reviews
                    context['o_follower_count'] = o_follower_count
                    context['o_lecture_delivered'] = o_lecture_delivered
                    context['expert_e'] = expert_e
                    context['expert_m'] = expert_m
                    context['expert_p'] = expert_p
                    context['expert_o'] = expert_o

                    try:
                        expert_online = ExpertOnlineStatus.objects.get(expert_id=expert_login.id).is_online
                    except:
                        expert_online = False
                    expert_follower = Expert_Following.objects.filter(Is_follow=1).filter(Is_follow_accepted=1).filter(Expert_id_id=expert_login.id)
                    expert_follower_count = expert_follower.count()
                    context['online'] = expert_online
                    news = CommonExpertNews.objects.filter(expert_id=expert_login.id)
                    skills = expert_login.Skill.split(',')
                    context['skills'] = skills
                    context['news'] = news
                    context['news_count'] = news.count()
                    context['expert_follower'] = expert_follower
                    context['expert_follower_count'] = expert_follower_count
                    return render(request, 'expert_index.html', context)
                else:
                    return HttpResponseRedirect(reverse('visitor'))
            else:
                return HttpResponseRedirect(reverse('visitor'))
        else:
            return HttpResponseRedirect(reverse('visitor'))

    except Exception as e:
        return HttpResponseRedirect(reverse('login'))


def show_expert_profile(request, expert_id=''):
    try:
        if request.user.is_authenticated:
            expert_login = check_expert_login(request.user.email)
            show_expert = Expert.objects.get(id=expert_id)
            try:
                expert_online = ExpertOnlineStatus.objects.get(expert_id=expert_login.id).is_online
            except:
                expert_online = False
            try:
                show_expert_online = ExpertOnlineStatus.objects.get(expert_id=show_expert.id).is_online
            except:
                show_expert_online = False
            show_expert_follower = Expert_Following.objects.filter(Is_follow=1).filter(Is_follow_accepted=1).filter(
                Expert_id_id=show_expert.id)
            expert_follower_count = show_expert_follower.count()
            from datetime import datetime, timedelta
            date_from = datetime.now() - timedelta(days=1)
            created_documents = AddLecture.objects.filter(
                expert_id_id=show_expert.id, update_timestamp__gte=date_from)

            context = dict()
            context['expert'] = expert_login
            context['show_expert'] = show_expert
            context['add_lect'] = created_documents
            context['online'] = expert_online
            context['show_expert_online'] = show_expert_online
            news = CommonExpertNews.objects.filter(expert_id=expert_login.id)
            skills = show_expert.Skill.split(',')
            context['skills'] = skills
            context['news'] = news
            context['news_count'] = news.count()
            context['expert_follower'] = show_expert_follower
            context['expert_follower_count'] = expert_follower_count
            return render(request, 'show_expert_profile.html', context)
    except Exception as e:
        return HttpResponseRedirect(reverse('visitor'))

def edit_expert(request):
    try:
        if request.user.is_authenticated:
            context = dict()
            expert_login = check_expert_login(request.user.email)
            context['each_expert'] = expert_login
            context['expert'] = expert_login
            try:
                expert_online = ExpertOnlineStatus.objects.get(expert_id=expert_login.id).is_online
            except:
                expert_online = False
            context['online'] = expert_online
            return render(request, 'edit_expert_profile.html', context)
        else:
            return HttpResponseRedirect(reverse('visitor'))
    except Exception as e:
        return None


def add_lecture(request):
    expert_exist = expert_exists(request.user.email)
    expert_login = check_expert_login(request.user.email)
    if request.method == 'POST':
        if expert_exist:
            # check whether it's valid:
            a = AddLecture.objects.create(title=request.POST['title'],description=request.POST['description'],
                                             time=request.POST['time'],date=request.POST['date'],expert_id_id=expert_login.id,update_timestamp=datetime.now())
            msg = expert_login.name + " has added new Lecture."
            expert_following = Expert_Following.objects.filter(Expert_id_id=expert_login.id).filter(Is_follow_accepted=1).filter(Is_follow=1)
            for each_expert in expert_following:
                CommonNews.objects.create(news=msg, student_id=each_expert.Student_id_id)
                NewsFeed.objects.create(news=msg, expert_id=expert_login.id,is_available=0)
            return HttpResponseRedirect('/expert_index/')
        else:
            return HttpResponseRedirect('/visitor/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AddLectureForm()
    context = dict()
    context['form'] = form
    context['expert'] = expert_login
    try:
        expert_online = ExpertOnlineStatus.objects.get(expert_id=expert_login.id).is_online
    except:
        expert_online = False
    context['online'] = expert_online
    return render(request, 'add_lectre.html', context)


def expert_history(request):
    try:
        user = check_auth(request)

        if user is not None:
            if user.is_active:
                login(request, user)
                context = dict()
                expert_login = check_expert_login(request.user.email)
                if expert_login:
                    add_lect = AddLecture.objects.filter(expert_id_id=expert_login.id)
                    context['expert'] = expert_login
                    context['add_lect'] = add_lect
                    try:
                        expert_online = ExpertOnlineStatus.objects.get(expert_id=expert_login.id).is_online
                    except:
                        expert_online = False
                    context['online'] = expert_online
                    return render(request, 'expert_lectre_history.html', context)
                else:
                    return HttpResponseRedirect('/visitor/')
    except Exception as e:
        return HttpResponseRedirect('/visitor/')


def student_index(request):
    try:
        user = check_auth(request)

        if user is not None:
            if user.is_active:
                context = dict()
                student_login = check_student_login(request.user.email)
                if student_login:
                    context['student'] = student_login
                    expert_m = Expert.objects.filter(Department='management')
                    expert_e = Expert.objects.filter(Department='engineering')
                    expert_p = Expert.objects.filter(Department='pharamacy')
                    context['expert_e'] = expert_e
                    context['expert_m'] = expert_m
                    context['expert_p'] = expert_p
                    context['online'] = True
                    context['MEDIA_ROOT'] = settings.MEDIA_ROOT
                    follower_m = []
                    follower_m_dict = dict()
                    follower_m_follow_status = []
                    follower_m_dict_follow_status = dict()
                    follower_e = []
                    follower_e_dict = dict()
                    follower_e_follow_status = []
                    follower_e_dict_follow_status = dict()
                    follower_p = []
                    follower_p_dict = dict()
                    follower_p_follow_status = []
                    lect_m_dict = dict()
                    lect_m = []
                    lect_p_dict = dict()
                    lect_p = []
                    lect_e_dict = dict()
                    lect_e = []
                    follower_p_dict_follow_status = dict()
                    for ex_m in expert_m:
                        is_ex_follower_m = Expert_Following.objects.filter(
                            Expert_id_id=ex_m.id).filter(Is_follow=1).filter(Is_follow_accepted=1)
                        follower_count = is_ex_follower_m.__len__()
                        lect_count = AddLecture.objects.filter(expert_id_id=ex_m.id)
                        if follower_count > 0:
                            follower_m_dict[ex_m.id] = follower_count
                            follower_m.append(follower_m_dict)
                        if lect_count:
                            lect_m_dict[int(ex_m.id)] = lect_count.__len__()
                            lect_m.append(lect_m_dict)
                        msg = check_follow_status(student_login.id,ex_m.id)
                        if msg:
                            follower_m_dict_follow_status[ex_m.id] = msg
                            follower_m_follow_status.append(follower_m_dict_follow_status)
                    for ex_e in expert_e:
                        is_ex_follower_e = Expert_Following.objects.filter(
                            Expert_id_id=ex_e.id).filter(Is_follow=1).filter(Is_follow_accepted=1)
                        follower_count = is_ex_follower_e.__len__()
                        if follower_count > 0:
                            follower_e_dict[ex_e.id] = follower_count
                            follower_e.append(follower_e_dict)
                        lect_count = AddLecture.objects.filter(expert_id_id=ex_e.id)
                        if lect_count:
                            lect_e_dict[int(ex_e.id)] = lect_count.__len__()
                            lect_e.append(lect_e_dict)
                        msg = check_follow_status(student_login.id, ex_e.id)
                        if msg:
                            follower_e_dict_follow_status[ex_e.id] = msg
                            follower_e_follow_status.append(follower_e_dict_follow_status)
                    for ex_p in expert_p:
                        is_ex_follower_p = Expert_Following.objects.filter(
                            Expert_id_id=ex_p.id).filter(Is_follow=1).filter(Is_follow_accepted=1)
                        follower_count = is_ex_follower_p.__len__()
                        if follower_count > 0:
                            follower_p_dict[ex_p.id] = follower_count
                            follower_p.append(follower_p_dict)
                        lect_count = AddLecture.objects.filter(expert_id_id=ex_p.id)
                        if lect_count:
                            lect_p_dict[int(ex_p.id)] = lect_count.__len__()
                            lect_p.append(lect_p_dict)
                        msg = check_follow_status(student_login.id, ex_p.id)
                        if msg:
                            follower_p_dict_follow_status[ex_p.id] = msg
                            follower_p_follow_status.append(follower_p_dict_follow_status)
                    context['follower_p'] = follower_p
                    context['follower_m'] = follower_m
                    context['follower_e'] = follower_e
                    context['follower_p_follow_status'] = follower_p_follow_status
                    context['follower_m_follow_status'] = follower_m_follow_status
                    context['follower_e_follow_status'] = follower_e_follow_status
                    context['lect_m'] = lect_m
                    context['lect_p'] = lect_p
                    context['lect_e'] = lect_e
                    news = CommonNews.objects.filter(student_id=student_login.id)
                    context['news'] = news
                    context['news_count'] = news.count()
                    following = Expert_Following.objects.filter(Student_id_id=student_login.id).filter(Is_follow_accepted=1).filter(Is_follow=1)
                    context['following_count'] = following.count()
                    context['following_experts'] = following
                    return render(request, 'student_index.html', context)
                else:
                    return HttpResponseRedirect(reverse('visitor'))
            else:
                return HttpResponseRedirect(reverse('visitor'))
        else:
            return HttpResponseRedirect(reverse('visitor'))

    except Exception as e:
        return HttpResponseRedirect(reverse('login'))

def check_follow_status(student_id,expert_id):
    try:
        is_follower_m = Expert_Following.objects.filter(Student_id_id=student_id).get(Expert_id_id=expert_id)
        if int(is_follower_m.Is_follow) == 1 and int(is_follower_m.Is_follow_accepted) == 1:
            msg = 'following'
        elif int(is_follower_m.Is_follow) ==1 and int(is_follower_m.Is_follow_accepted) == 0:
            msg = 'requested'
        else:
            msg = 'follow'
        return msg
    except Exception as e:
        return None


def send_follow_request(request, expert_id):
    try:
        user = check_auth(request)

        if user is not None:
            if user.is_active:
                login(request, user)
                context = dict()
                student_login = check_student_login(request.user.email)
                if student_login:
                    ex = Expert_Following.objects.update_or_create(Student_id_id=student_login.id,Expert_id_id=expert_id,Is_follow=1,Is_follow_accepted=0)
                    msg = student_login.name + " has sent you follow request."
                    CommonExpertNews.objects.create(news=msg, expert_id=expert_id,is_available=False)
                    context = dict()
                    context['ex'] = ex
                    return HttpResponse(context)
                else:
                    return HttpResponseRedirect(reverse('visitor'))
    except Exception as e:
        return HttpResponseRedirect(reverse('login'))


def student_edit_profile(request):
    try:
        if request.user.is_authenticated:
            context = dict()
            student_login = check_student_login(request.user.email)
            context['each_student'] = student_login
            context['student'] = student_login

            return render(request, 'edit_student_profile.html', context)
        else:
            return HttpResponseRedirect(reverse('visitor'))
    except Exception as e:
        return None


def student_following_list(request):
    try:
        user = check_auth(request)
        if user is not None:
            if user.is_active:
                login(request, user)
                context = dict()
                student_login = check_student_login(request.user.email)
                if student_login:
                    expert_list = []
                    experts = Expert_Following.objects.filter(Student_id_id=student_login.id).filter(Is_follow=1).filter(Is_follow_accepted=1)
                    for expert in experts:
                        a = expert.Expert_id
                        expert_list.append(Expert.objects.get(id=a.id))
                context['experts'] = expert_list
                context['each_student'] = student_login
                context['student'] = student_login
                return render(request, 'student_following.html', context)
    except Exception as e:
        return HttpResponseRedirect(reverse('visitor'))


def student_history(request):
    try:
        user = check_auth(request)
        if user is not None:
            if user.is_active:
                login(request, user)
                context = dict()
                lecture_hist = []
                student_login = check_student_login(request.user.email)
                if student_login:
                    lecture_history = StudentLectureAttended.objects.filter(student_id_id=student_login.id)
                    for each_lect in lecture_history:
                        lectr = AddLecture.objects.filter(id=each_lect.lecture_id.id)
                        lecture_hist.append(lectr)
                    context['lecture_history'] = lecture_hist
                context['each_student'] = student_login
                context['student'] = student_login

                return render(request, 'student_history.html', context)

    except Exception as e:
        return HttpResponseRedirect(reverse('visitor'))


def update_student(request):
    try:
        # if this is a POST request we need to process the form data
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = StudentForm(request.POST)
            # check whether it's valid:
            try:
                student_exist = student_exists(request.user.email)
            except:
                student_exist = student_exists(request.POST['Personal_Email'])
            first_name = get_first_name(request.POST['name'])
            last_name = get_last_name(request.POST['name'])
            # create the folder if it doesn't exist.
            folder = request.path
            try:
                uploaded_filename = request.FILES['Profile_piture'].name
                file = request.FILES['Profile_piture']
            except:
                if student_exist:
                    file = Student.objects.get(Personal_Email=request.user.email).Profile_piture

            # save the uploaded file inside that folder.
            if student_exist:
                s = Student.objects.filter(Personal_Email=request.user.email).update(name=request.POST['name'],
                                                                                 Collage=request.POST['Collage'],
                                                                                 Year_Experience=request.POST['Year_Experience'],
                                                                                 Qualification=request.POST['Qualification'],
                                                                                 mobile=request.POST['mobile'],
                                                                                 Profile_piture=file,
                                                                                 password=request.POST['password'])

                MyProfileForm = StudentForm(request.POST, request.FILES)

                profile = Student.objects.get(Personal_Email=request.user.email)
                profile.Profile_piture = file
                profile.save()
                u = User.objects.filter(email=request.user.email).update(password=hasher.encode(password=request.POST['password'],
                                                               salt='salt',
                                                               iterations=50000), is_active=1, is_staff=0,
                                        is_superuser=0, first_name=first_name, last_login=datetime.today(),
                                        last_name=last_name,
                                        date_joined=datetime.today())
            else:
                if form.is_valid():
                    form.save()

                    u = User.objects.create(password=hasher.encode(password=request.POST['password'],
                                                                   salt='salt',
                                                                   iterations=50000), is_active=1, is_staff=0,
                                            is_superuser=0, first_name=first_name, last_login=datetime.today(),
                                            last_name=last_name, email=request.POST['Personal_Email'],
                                            username=generate_username(first_name, last_name), date_joined=datetime.today())

        context = dict()
        student_login = check_student_login(request.user.email)
        context['each_student'] = student_login
        context['student'] = student_login

        return render(request, 'edit_student_profile.html', context)

    except Exception as e:
        return HttpResponseRedirect('/visitor/')


def notification_student(request):
    try:
        user = check_auth(request)

        if user is not None:
            if user.is_active:
                context = dict()
                student_login = check_student_login(request.user.email)
                if student_login:
                    context['student'] = student_login
                    news = CommonNews.objects.filter(student_id=student_login.id)
                    context['news'] = news
                    context['news_count'] = news.count()
                    return render(request, 'notification_student.html', context)
        else:
            return HttpResponseRedirect(reverse('visitor'))
    except Exception as e:
        return HttpResponseRedirect(reverse('visitor'))


def notification_expert(request):
    try:
        user = check_auth(request)
        if user is not None:
            if user.is_active:
                context = dict()
                student_login = check_expert_login(request.user.email)
                if student_login:
                    context['expert'] = student_login
                    news = CommonExpertNews.objects.filter(expert_id=student_login.id)
                    context['news'] = news
                    context['news_count'] = news.count()
                    try:
                        expert_online = ExpertOnlineStatus.objects.get(expert_id=student_login.id).is_online
                    except:
                        expert_online = False
                    context['online'] = expert_online
                    return render(request, 'notification_expert.html', context)
        else:
            return HttpResponseRedirect(reverse('visitor'))
    except Exception as e:
        return HttpResponseRedirect(reverse('visitor'))


def clear_notification_student(request):
    try:
        context = dict()
        id = request.GET['id']
        news = CommonNews.objects.filter(id=int(id)).delete()
        context['news'] = news
        return HttpResponse(context)
    except Exception as e:
        return HttpResponseRedirect(reverse('login'))


def clear_notification_expert(request):
    try:
        context = dict()
        id = request.GET['id']
        news = CommonExpertNews.objects.filter(id=int(id)).delete()
        context['news'] = news
        return HttpResponse(context)
    except Exception as e:
        return HttpResponseRedirect(reverse('login'))


def clear_notification_expert_all(request):
    try:
        context = dict()
        news = CommonExpertNews.objects.all().delete()
        return HttpResponseRedirect('/expert_index/')
    except Exception as e:
        return HttpResponseRedirect(reverse('login'))


def clear_notification_student_all(request):
    try:
        context = dict()
        news = CommonNews.objects.all().delete()
        return HttpResponseRedirect('/student_index/')
    except Exception as e:
        return HttpResponseRedirect(reverse('login'))


def send_email(request):
    try:
        from django.core.mail import EmailMessage
        from django.core.mail import send_mail
        send_mail('Testing', 'Testing', settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
        # email = EmailMessage('Testing', 'Testing', to=['komalmehta.8380@gmail.com'])
        # email.send()
        return HttpResponseRedirect('/visitor/')
    except Exception as e:
        return HttpResponseRedirect(reverse('login'))


def expert_online_status(request):
    try:
        if ExpertOnlineStatus.objects.filter(expert_id=request.GET['expert_id']):
            a = ExpertOnlineStatus.objects.filter(expert_id=request.GET['expert_id']).update(is_online=bool(int(request.GET['status'])))
        else:
            a = ExpertOnlineStatus.objects.create(is_online=bool(int(request.GET['status'])),expert_id=request.GET['expert_id'])
        context = dict()
        context["online"] = bool(request.GET['status'])
        expert = Expert.objects.get(id=request.GET['expert_id'])
        if NewsFeed.objects.filter(expert_id=request.GET['expert_id']).filter(is_available=1):
            NewsFeed.objects.filter(expert_id=request.GET['expert_id']).get(is_available=1).delete()
        else:
            if bool(int(request.GET['status'])):
                msg = expert.name + " is available."
                NewsFeed.objects.create(news=msg,expert_id=request.GET['expert_id'],is_available=1)
        return HttpResponse(context)
    except Exception as e:
        return HttpResponseRedirect('/visitor/')

def review_expert(request):
    user = check_auth(request)
    if user is not None:
        if user.is_active:
            context = dict()
            student_login = check_expert_login(request.user.email)
            if student_login:
                context['each_expert'] = student_login

                news = CommonExpertNews.objects.filter(expert_id=student_login.id)
                context['news'] = news
                context['news_count'] = news.count()
            return render(request, 'expert_review.html', context)
            pass


def student_review(request):
    user = check_auth(request)

    if user is not None:
        if user.is_active:
            context = dict()
            student_login = check_student_login(request.user.email)
            # data = request.GET['data[]']
            # for i in range(len(data)):
            #     data[i] = int(data[i])
            # sumd = sum(data) / len(data)
            # overall = min(data, key=lambda x: abs(x-sumd))
            if student_login:
                pass
                # if StudentReview.objects.filter(student_id=student_login.id):
                #     StudentReview.objects.filter(student_id=student_login.id).update(
                #         communication_skill=data[0], behaviour=data[4], domain_knowledge=data[1],
                #         team_skill=data[2], open_for_learning=data[3], overall=overall)
                # else:
                #     StudentReview.objects.create( communication_skill=data[0], behaviour=data[4], domain_knowledge=data[1],
                #         team_skill=data[2], open_for_learning=data[3], overall=overall, student_id=student_login.id)
                context['student'] = student_login
                news = CommonNews.objects.filter(student_id=student_login.id)
                context['news'] = news
                context['news_count'] = news.count()
                return render(request, 'student_review.html', context)

def student_review_show(request):
    user = check_auth(request)

    if user is not None:
        if user.is_active:
            context = dict()
            student_login = check_student_login(request.user.email)
            context['student'] = student_login
            news = CommonNews.objects.filter(student_id=student_login.id)
            context['news'] = news
            context['news_count'] = news.count()
            return render(request, 'student_review.html', context)


def user_admin(request):
    user = check_auth(request)
    if user is not None:
        if user.is_active:
            context = dict()
            expert_request = []
            expert_active = []
            student = Student.objects.all()
            student_count = student.count()
            experts = Expert.objects.all()
            for each_expert in experts:
                expert = User.objects.get(email=each_expert.Personal_Email)
                if expert.is_active == 0:
                    expert_request.append(each_expert)
                else:
                    expert_active.append(each_expert)
            active_expert_count = expert_active.__len__()
            expert_request_count = expert_request.__len__()
            active_user_count = student_count + active_expert_count
            block_student = Student_block_count.objects.all()
            block_student_count = block_student.count()
            news = AdminNews.objects.all()
            context['student_count'] = student_count
            context['active_expert_count'] = active_expert_count
            context['expert_request_count'] = expert_request_count
            context['active_user_count'] = active_user_count
            context['expert_request'] = expert_request
            context['expert_active'] = expert_active
            context['student'] = student
            context['block_student'] = block_student
            context['block_student_count'] = block_student_count
            context['news'] = news
            return render(request, 'user_admin.html', context)


def accept_expert(request, expert_id=''):
    user = check_auth(request)
    if user is not None:
        if user.is_active:
            login(request, user)
            context = dict()
            expert_email = Expert.objects.get(id=expert_id).Personal_Email
            is_ex_follower = User.objects.filter(email=expert_email).update(is_active=1)
            return HttpResponseRedirect('/user_admin/')
        else:
            return HttpResponseRedirect(reverse('visitor'))
    else:
        return HttpResponseRedirect(reverse('visitor'))


def reject_expert(request, expert_id=''):
    user = check_auth(request)
    if user is not None:
        if user.is_active:
            login(request, user)
            context = dict()
            expert_email = Expert.objects.get(id=expert_id)
            is_ex_follower = User.objects.filter(email=expert_email.Personal_Email).delete()
            expert_email.delete()
            return HttpResponseRedirect('/user_admin/')
        else:
            return HttpResponseRedirect(reverse('visitor'))
    else:
        return HttpResponseRedirect(reverse('visitor'))


def reject_student(request, expert_id=''):
    user = check_auth(request)
    if user is not None:
        if user.is_active:
            login(request, user)
            context = dict()
            student_email = Student.objects.get(id=expert_id)
            is_ex_follower = User.objects.filter(email=student_email.Personal_Email).delete()
            student_email.delete()
            return HttpResponseRedirect('/user_admin/')
        else:
            return HttpResponseRedirect(reverse('visitor'))
    else:
        return HttpResponseRedirect(reverse('visitor'))


def reset_student_block_count(request, student_id=''):
    user = check_auth(request)
    if user is not None:
        if user.is_active:
            login(request, user)
            context = dict()
            student = Student_block_count.objects.filter(Student_id_id=student_id).update(block_count=0)
            return HttpResponseRedirect('/user_admin/')
        else:
            return HttpResponseRedirect(reverse('visitor'))
    else:
        return HttpResponseRedirect(reverse('visitor'))


def expert_enq(request, expert_id='', student_id=''):
    try:
        set_record = ExpertEnq.objects.update_or_create(expert_id=expert_id,student_id=student_id)
        record_exists = ExpertEnq.objects.filter(expert_id=expert_id)
        expert = Expert.objects.get(id=expert_id)
        student = Student.objects.get(id=student_id)
        msg = student.name + ' (Email: ' + student.Personal_Email + ') has sent enquiry for expert ' + expert.name + ' (Email: ' + expert.Personal_Email + ')'
        AdminNews.objects.create(news=msg, expert_id=expert_id, student_id=student_id)
        if record_exists:
            record_count = record_exists.count()
            if record_count >= 5:
                msg = student.name + ' (Email: ' + student.Personal_Email+') has sent enquiry for expert ' + expert.name +' (Email: ' + expert.Personal_Email +')'
                AdminNews.objects.create(news=msg, expert_id=expert_id, student_id=student_id)
        context= dict()
        context['msg'] = 'You have successfully sent enquiry to admin'
        return HttpResponse(context)

    except Exception as e:
        return None

def set_expert_review(request, expert_id='', student_id= ''):
    ExpertReview.objects.update_or_create(as_boss=1,expert_id=expert_id,student_id=student_id)
    return HttpResponse(None)
