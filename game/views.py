import random
from django.contrib import messages
from django.shortcuts import render, redirect
from game.models import Game, Move

# just for showing icons in templates
icons = {"Rock": "<i class='fa-solid fa-hand-back-fist'></i>", "Paper":"<i class='fa-solid fa-hand'></i>",  "Scissors":"<i class='fa-solid fa-hand-scissors'></i>"}


# preventing a user from starting a game without player names entered
def get_referer(request):
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return None
    return referer


# and an error page to show in this case
def custom_permission_denied_view(request):
    return render(request, "errors/403.html", {})


# the main view to show previous game results
def home(request, last=10):
    games = Game.objects.filter().order_by('-id')[:last]
    return render(request, 'home.html', context={'games': games})


# showing last N moves and results for a game selected
def see_moves(request, game_id, last=15):
    game = Game.objects.get(pk=game_id)
    moves = Move.objects.filter(game_id=game_id).order_by('-id')[:last]
    for move in  moves:
        move.icon1 = icons[move.player1_choice]
        move.icon2 = icons[move.player2_choice]
    return render(request, 'moves.html', context={'moves': moves, 'game':game})


# creating a new game instance when player names are entered
def create_game(request, option):
    with_computer = False
    if option == "computer":
        with_computer = True

    if request.method == "POST":
        name1 = request.POST.get('name1')
        if not with_computer:
            name2 = request.POST.get('name2')
        else:
            name2 = "Computer"

        game = Game(player1_name=name1, player2_name=name2, with_computer=with_computer)
        game.save()

        # clearing the session from previous games
        request.session.flush()
        request.session['game'] = game.pk
        # calling the play method with a game instance stored in a session
        return redirect("play_game")

    else:
        # passing with_computer boolean variable to template to only show one player in this case
        return render(request, 'input_names.html', context={'with_computer': with_computer})


# just determining the winner based on player choices
def get_winner(ch1, ch2, name1, name2):
    if ch1 == ch2:
        return "Tie"
    elif ch1 == "Rock" and ch2 == "Scissors":
        return name1
    elif ch1 == "Rock" and ch2 == "Paper":
        return name2
    elif ch1 == "Paper" and ch2 == "Rock":
        return name1
    elif ch1 == "Paper" and ch2 == "Scissors":
        return name2
    elif ch1 == "Scissors" and ch2 == "Rock":
        return name2
    elif ch1 == "Scissors" and ch2 == "Paper":
        return name1


# the main logics method
def play_game(request):
    round_completed = False
    # getting a game instance from sessions
    game = Game.objects.get(pk=request.session['game'])
    # checking if a user didn't by chance try to come here directly (without entering names)
    if not get_referer(request):
        return custom_permission_denied_view(request)

    # for showing current turn name in template
    turn = game.player1_name
    if request.method == "POST":
        # if first player already chose or when it's a play with computer
        if 'player1_move' in request.session or game.with_computer:
            if game.with_computer:
                move1 = request.POST.get('move')
                # randomly choosing a move
                move2 = random.choice(["Rock", "Paper", "Scissors"])
            else:
                move1 = request.session['player1_move']
                move2 = request.POST.get('move')

            # using Django's messages framework to pass info to the template
            messages.info(request, "" + game.player1_name + ": " + move1 + " " + icons[move1] +
                          "&nbsp;&nbsp;|&nbsp;&nbsp;" + "" + game.player2_name + ": " + move2 + " " + icons[move2])
            winner = get_winner(move1, move2, game.player1_name, game.player2_name)

            # saving a new move instance with outcomes
            new_move = Move(game=game,player1_choice=move1,player2_choice=move2,winner=winner)
            new_move.save()
            if winner == "Tie":
                messages.success(request, 'It is a tie!')
            else:
                messages.success(request, winner+' wins!')

            # to show start again/quit buttons in template when a round is complete
            round_completed = True

            # clearing the session from a previous move
            if "player1_move" in request.session:
                del request.session["player1_move"]

        else:
            # when a first player made a move, storing it in session
            request.session['player1_move'] = request.POST.get('move')
            turn = game.player2_name

    return render(request, 'game.html', context={'round_completed': round_completed,
                                                 'game_description': str(game),
                                                 'turn':turn})


# when a user wants to continue an already existing name
def continue_game(request, game_id):
    # clearing the session from previous games
    request.session.flush()
    # storing a game id from url in session
    request.session['game'] = game_id
    return redirect("play_game")

