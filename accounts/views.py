from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from .forms import SignupForm, LoginForm
from accounts.models import Account
from django.contrib.auth import get_user_model
from chats.models import Conversation, CustomGroups
from datetime import datetime, date, timedelta
from django.db.models import Q
from time import sleep
from django.core.serializers import serialize, deserialize
from json import loads, dumps
from django.db import connection

USER_MODEL = get_user_model()


def get_chat_data(request, friend_username):  # make this more secure later
    connection.queries_log.clear()
    if request.user and Account.objects.filter(user__username=friend_username).exists():     # especially here
        user_acc = Account.objects.get(user=request.user)
        friend_acc = Account.objects.get(user__username=friend_username)

        conversations = Conversation.objects.filter(Q(participant_1=user_acc) | Q(participant_2=user_acc)).filter(Q(participant_1=friend_acc) | Q(participant_2=friend_acc))
        if conversations:
            conversation = conversations.first()
            messages = conversation.messages.all().order_by('date_created')

            data = {"message_date": {},
                    "profile_pic_url": f"{friend_acc.profile_picture.url}",
                    "first_name": f"{friend_acc.user.first_name}",
                    "last_name": f"{friend_acc.user.last_name}"}

            for msg in messages:
                msg_data = {
                    "text": msg.message_text,
                    "sender": msg.sender.user.username,
                    "recipient": msg.recipient.user.username,
                    "time_created": msg.date_created.time().strftime("%H:%M")
                }

                date_created = msg.date_created.date()
                if date_created == date.today():
                    date_created = "today"

                elif (date.today() - date_created) == timedelta(1):
                    date_created = "yesterday"

                else:
                    date_created = date_created.strftime("%d-%m-%Y")

#                list of same date messages creation

                if not data["message_date"].get(date_created, None):
                    data["message_date"][date_created] = [msg_data]

                else:
                    data["message_date"].get(date_created).append(msg_data)
            # print(data)

            print("\n--- SQL QUERIES ---")
            for q in connection.queries:
                print(q["time"], q["sql"])

            print("TOTAL:", len(connection.queries))
            return JsonResponse(data)

    return JsonResponse({})


def home_page(request):
    context = {}
    if request.user.is_authenticated:
        user = request.user
        user_account = Account.objects.get(user=user)
        user_profile_pic_url = user_account.profile_picture.url
        context["user_profile_pic_url"] = user_profile_pic_url

        # logic to get conversations relating to the authenticated user

        conversations = Conversation.objects.all().filter(Q(participant_1=user_account) | Q(participant_2=user_account)).order_by("-timestamp")
        list_of_gist_partners = []
        user_convo = {}

        for convo in conversations:
            convo_data = {}
            if convo.timestamp.date() == date.today():
                convo_data["timestamp"] = convo.timestamp.time().strftime("%H:%M")

            else:
                convo_data["timestamp"] = convo.timestamp.date().strftime("%d/%m/%Y")

            convo_data["conversation_model"] = convo

            if convo.participant_1 == user_account:
                list_of_gist_partners.append(str(convo.participant_2))
                convo_data["account_model"] = convo.participant_2
                user_convo[str(convo.participant_2)] = convo_data

            elif convo.participant_2 == user_account:
                list_of_gist_partners.append(str(convo.participant_1))
                convo_data["account_model"] = convo.participant_1
                user_convo[str(convo.participant_1)] = convo_data


        groups = user_account.member_custom_group.all().order_by("-timestamp")

        context["user_convo"] = user_convo
        context["gist_partners"] = list_of_gist_partners
        context["today"] = date.today()
        context["groups"] = groups

    return render(request, 'base.html', context)


def login_page(request):
    context = {}
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST) 

        if form.is_valid():
            data = form.cleaned_data
            username = data.get("username")
            password = data.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session["username"] = user.username
                print(f"{user} signed in")
                return redirect('/')

        else:
            print("Yo wrong login credentials")

    context["form"] = form
    return render(request, 'accounts/login.html', context)


def logout_page(request):
    username = request.session.get("username")
    logout(request)
    print(f"{username} signed out")
    return redirect('/')


def signup_page(request):
    context = {}
    form = SignupForm()

    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            print("signup form is valid")

            form = SignupForm()

            return redirect('/')

        else:
            print("signup form is not valid")

    context["form"] = form
    return render(request, 'accounts/signup.html', context)

def profile_search_page(request):
    context = {}
    return render(request, 'profile-search.html', context)
