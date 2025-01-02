from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import ChangeUsernameForm, ChangePasswordForm, AddEmailForm
from main.api import find_clan_with_tag, get_clan_badge, clean_tag, get_member_data, get_all_clan_data, get_all_player_data
from .models import SavedClan, SavedPlayer, GlobalPlayer, GlobalClan
from main.api import *
from .helpers import determine_email_level
from register.send_emails import send_verification_email

def home(request):
    context = {
        'is_logged_in': request.user.is_authenticated,
        'user': request.user if request.user.is_authenticated else None,
    }
    return render(request, "main/home.html", context)

@login_required(login_url='/')
def settings(request):
    return render(request, "main/settings.html", {"email_level": determine_email_level(request.user)})

@login_required(login_url='/')
def logout_view(request):
    logout(request)
    return redirect("home")

@login_required(login_url='/')
def delete_account(request):
    request.user.delete()
    return redirect("home")

@login_required(login_url='/')
def change_username(request):
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST)
        if form.is_valid():
            new_username = form.cleaned_data['new_username']
            password = form.cleaned_data['password']
            
            # Authenticate the user with the provided password
            user = authenticate(username=request.user.username, password=password)
            if user is not None:
                # If password is correct, update the username
                request.user.username = new_username
                request.user.save()
                return render(request, "main/settings.html", {"email_level": determine_email_level(request.user), "message": "Username changed successfully!"})
            else:
                form.add_error('password', 'Incorrect password')
    else:
        form = ChangeUsernameForm()

    return render(request, 'main/change_username.html', {'form': form})

@login_required(login_url='/')
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']
            confirm_new_password = form.cleaned_data["confirm_new_password"]
            if new_password != confirm_new_password:
                return render(request, 'main/change_password.html', {'form': form, "success_message": "Passwords do not match", "is_error": True})
            
            # Authenticate user with current password
            user = authenticate(username=request.user.username, password=current_password)
            if user is not None:
                # Update the user's password
                user.set_password(new_password)
                user.save()

                # Re-authenticate the user to update session authentication
                update_session_auth_hash(request, user)

                return render(request, "main/settings.html", {"email_level": determine_email_level(request.user), "message": "Password changed successfully!"})
            else:
                form.add_error('current_password', 'Incorrect current password')
    else:
        form = ChangePasswordForm()

    return render(request, 'main/change_password.html', {'form': form})

@login_required(login_url='/')
def add_email(request):
    form = AddEmailForm(request.POST or None)
    
    if form.is_valid():
        email = form.cleaned_data['email']
        request.user.email = email
        request.user.save()
        send_verification_email(request.user, request)
        return render(request, "main/settings.html", {"email_level": determine_email_level(request.user), "message": "Email added succesfully. Please verify it by checking your inbox."})
    
    return render(request, 'main/add_email.html', {"form": form})

@login_required(login_url='/')
def resend_verification_email(request):
    send_verification_email(request.user, request)
    return render(request, "main/settings.html", {"email_level": determine_email_level(request.user), "message": "Check your inbox for a link to verify your email"})
    

def clan_search(request):
    in_database = "not_logged_in"
    if request.method == "POST":
        search_type = request.POST.get("search_type") 
        if search_type == "clan":
            old_tag = clean_tag(request.POST.get("clan_tag"))
            try:
                # raise ValueError(f"Invalid search type: {find_clan_with_tag(old_tag)}")
                clan_name, clan_tag, clan_type, clan_description, clan_members, clan_points = find_clan_with_tag(old_tag, ["name", "tag", "type", "description", "members", "clanPoints"])
                clan_badge = get_clan_badge(old_tag)
                if request.user.is_authenticated:
                    if SavedClan.objects.filter(user=request.user, clan_tag=old_tag).first():
                        in_database = True
                    else:
                        in_database = False
            except IndexError:
                return render(request, "main/clan_search.html", {"error": "clan"})
            return render(request, "main/clan_search.html", {"clan_name": clan_name, "clan_tag": clan_tag, "clan_type": clan_type,
                        "clan_description": clan_description, "clan_members": clan_members, "clan_points": clan_points, "clan_badge": clan_badge, "saved": in_database})
        else:
            tag = clean_tag(request.POST.get("clan_tag"))
            player_data = get_all_player_data(clean_tag(tag))
            if request.user.is_authenticated:
                if SavedPlayer.objects.filter(user=request.user, player_tag=tag).first():
                    in_database = True
                else:
                    in_database = False
            if player_data == {'reason': 'notFound'}:
                return render(request, "main/clan_search.html", {"error": "player", "player_data": "error"})
            return render(request, "main/clan_search.html", {"player_data": player_data, "saved": in_database})
    return render(request, "main/clan_search.html")


@login_required(login_url='/')
def toggle_save_clan(request, clan_tag):
    saved_clan = SavedClan.objects.filter(user=request.user, clan_tag=clean_tag(clan_tag)).first()
    clan_data = get_all_clan_data(clean_tag(clan_tag))
    member_data = get_member_data(clean_tag(clan_tag))
    is_being_tracked = GlobalClan.objects.filter(clan_tag=clean_tag(clan_tag)).exists()
    if request.user.is_authenticated:
        saved_clan_count = SavedClan.objects.filter(user=request.user).count()
    change = None

    if saved_clan:
        saved_clan.delete()
        change = "clan_removed"
    elif saved_clan_count < 5:
        SavedClan.objects.create(user=request.user, clan_tag=clean_tag(clan_tag))
        change = "clan_saved"
    else:
        change = "too_many_clans"

    is_saved = "not_logged_in"
    if request.user.is_authenticated:
        if SavedClan.objects.filter(user=request.user, clan_tag=clean_tag(clan_tag)).first():
            is_saved = True
        else:
            is_saved = False

    return render(request, "main/view_clan.html", {"member_data": member_data, "clan_tag": clan_tag, "mode": "general", "clan_data": clan_data, "is_being_tracked": is_being_tracked, "change": change, "is_saved": is_saved})


@login_required(login_url='/')
def toggle_save_player(request, player_tag):
    player = get_all_player_data(clean_tag(player_tag))
    saved_player = SavedPlayer.objects.filter(user=request.user, player_tag=clean_tag(player_tag)).first()
    is_being_tracked = GlobalPlayer.objects.filter(player_tag=clean_tag(player_tag)).exists()
    saved_player_count = SavedPlayer.objects.filter(user=request.user).count()
    change = None

    if saved_player:
        saved_player.delete()
        change = "player_removed"
    elif saved_player_count < 10:
        SavedPlayer.objects.create(user=request.user, player_tag=clean_tag(player_tag))
        change = "player_saved"
    else:
        change = "too_many_players"

    is_saved = "not_logged_in"
    if request.user.is_authenticated:
        if SavedPlayer.objects.filter(user=request.user, player_tag=clean_tag(player_tag)).first():
            is_saved = True
        else:
            is_saved = False

    return render(request, "main/view_player.html", {"player": player, "is_being_tracked": is_being_tracked, "change": change, "is_saved": is_saved})


@login_required(login_url='/')
def my_clans(request):
    clans_data = []

    # Iterate through each saved clan for the logged-in user
    for clan in SavedClan.objects.filter(user=request.user):
        clan_info = find_clan_with_tag(clean_tag(clan.clan_tag), ["name", "tag", "type", "description", "members", "clanPoints"])
        clan_badge = get_clan_badge(clean_tag(clan.clan_tag))
        
        # Prepare the data to pass to the template
        clans_data.append({
            'name': clan_info[0],
            'tag': clan_info[1],
            'type': clan_info[2],
            'description': clan_info[3],
            'members': clan_info[4],
            'clan_points': clan_info[5],
            'badge': clan_badge,
        })

    return render(request, "main/my_clans.html", {'clans': clans_data})

def view_clan(request, clan_tag, mode):
    is_saved = "not_logged_in"
    change = None
    member_data = get_member_data(clean_tag(clan_tag))
    clan_data = get_all_clan_data(clean_tag(clan_tag))
    is_being_tracked = GlobalClan.objects.filter(clan_tag=clean_tag(clan_tag)).exists()
    if request.user.is_authenticated:
        saved_clan_count = SavedClan.objects.filter(user=request.user).count()

    save_clan = request.POST.get('save_clan', 'no')
    unsave_clan = request.POST.get('unsave_clan', 'no')
    
    if request.user.is_authenticated:
        if SavedClan.objects.filter(user=request.user, clan_tag=clean_tag(clan_tag)).first():
            is_saved = True
        else:
            is_saved = False

    if save_clan == "yes":
        if saved_clan_count < 10:
            new_clan = SavedClan(user=request.user, clan_tag=clean_tag(clan_tag))
            new_clan.save()
            change = "clan_saved"
        else:
            change = "too_many_clans"
        is_saved = True
    if unsave_clan == "yes":
        old_clan = SavedClan.objects.get(user=request.user, clan_tag=clean_tag(clan_tag))
        old_clan.delete()
        change = "clan_removed"
        is_saved = False

    if mode not in ["general", "home_village", "builder_base", "all"]:
        mode = "general"

    if request.method == "POST" and not is_being_tracked:
        if 'track_clan_history' in request.POST:
            new_clan = GlobalClan(clan_tag=clean_tag(clan_tag))
            new_clan.save() 
            is_being_tracked = True
            for player in member_data["items"]:
                tag = player["tag"]
                player_is_being_tracked = GlobalPlayer.objects.filter(player_tag=clean_tag(tag)).exists()
                if not player_is_being_tracked:
                    new_player = GlobalPlayer(player_tag=clean_tag(tag))
                    new_player.save() 
    return render(request, "main/view_clan.html", {"member_data": member_data, "clan_tag": clan_tag, "mode": mode, "clan_data": clan_data, 
                                                   "is_being_tracked": is_being_tracked, "is_saved": is_saved, "change": change})

@login_required(login_url='/')
def my_players(request):
    players_data = []
    for player in SavedPlayer.objects.filter(user=request.user):
        data = get_all_player_data(clean_tag(player.player_tag))
        players_data.append(data)

    return render(request, "main/my_players.html", {'players': players_data})

def view_player(request, player_tag):
    is_saved = "not_logged_in"
    change = None
    player = get_all_player_data(clean_tag(player_tag))
   # is_being_tracked = GlobalPlayer.objects.filter(player_tag=clean_tag(player_tag)).exists()
    if request.user.is_authenticated:
        saved_player_count = SavedPlayer.objects.filter(user=request.user).count()
        if SavedPlayer.objects.filter(user=request.user, player_tag=clean_tag(player_tag)).first():
            is_saved = True
        else:
            is_saved = False

    save_player = request.POST.get('save_player', 'no')
    unsave_player = request.POST.get('unsave_player', 'no')
    start_tracking_player = request.POST.get('start_tracking_player', 'no')
    print(save_player, unsave_player, start_tracking_player)
    if start_tracking_player == "yes":
        new_player = GlobalPlayer(player_tag=clean_tag(player_tag))
        new_player.save() 
        is_being_tracked = True
    if save_player == "yes":
        if saved_player_count < 10:
            new_player = SavedPlayer(user=request.user, player_tag=clean_tag(player_tag))
            new_player.save()
            change = "player_saved"
        else:
            change = "too_many_players"
        is_saved = True
    if unsave_player == "yes":
        old_player = SavedPlayer.objects.get(user=request.user, player_tag=clean_tag(player_tag))
        old_player.delete()
        change = "player_removed"
        is_saved = False
    return render(request, "main/view_player.html", {"player": player, "is_being_tracked": is_being_tracked, "is_saved": is_saved, "change": change})


def view_player_history(request, player_tag):
    player = get_all_player_data(clean_tag(player_tag))
    player_history = GlobalPlayer.objects.get(player_tag=clean_tag(player_tag))
    monthly_data = player_history.monthly_data.all()[::-1]
    if len(monthly_data) == 0:
        monthly_data = "N/A"

    return render(request, "main/view_player_history.html", {"player": player, "monthly_data": monthly_data})

def view_clan_general_history(request, clan_tag):
    clan = get_all_clan_data(clean_tag(clan_tag))
    clan_general_history = GlobalClan.objects.get(clan_tag=clean_tag(clan_tag))
    monthly_data_general = clan_general_history.monthly_data_general.all()[::-1]
    if len(monthly_data_general) == 0:
        monthly_data_general = "N/A"

    type_of_data = request.POST.get('type_of_data', 'in-depth')
    type_of_member_data = request.POST.get('type_of_member_data', 'general')

    summary_member_data = []
    members = clan["memberList"]
    for member in members:
        player_tag = clean_tag(member["tag"])
        player, created = GlobalPlayer.objects.get_or_create(player_tag=player_tag)
        for month in player.monthly_data.all():
            summary_member_data.append(month)

    return render(request, "main/view_clan_general_history.html", 
                  {"clan": clan, "monthly_data_general": monthly_data_general, "summary_member_data": summary_member_data,
                   "type_of_data": type_of_data, "type_of_member_data": type_of_member_data})


def view_clan_war_history(request, clan_tag):
    clan = get_all_clan_data(clean_tag(clan_tag))
    clan_war_history = GlobalClan.objects.get(clan_tag=clean_tag(clan_tag))
    monthly_data_war = clan_war_history.monthly_data_war.all()[::-1]
    each_war_data = clan_war_history.war_information.all()[::-1]
    if len(each_war_data) == 0:
        each_war_data = "N/A"
    
    # Get the submitted values or use defaults
    type_of_war = request.POST.get('type_of_war', 'regular')  # Default value if none selected
    type_of_data = request.POST.get('type_of_data', 'summary')
    include_member_data = request.POST.get('include_member_data', 'yes')

    summary_member_data = []
    members = clan["memberList"]
    for member in members:
        player_tag = clean_tag(member["tag"])
        player, created = GlobalPlayer.objects.get_or_create(player_tag=player_tag)
        for month in player.monthly_data_war.all():
            summary_member_data.append(month)


    return render(request, "main/view_clan_war_history.html", {
        "clan": clan,
        "monthly_data_war": monthly_data_war,
        "each_war_data": each_war_data,
        "type_of_war": type_of_war,
        "type_of_data": type_of_data,
        "include_member_data": include_member_data,
        "summary_member_data": summary_member_data,
    })

