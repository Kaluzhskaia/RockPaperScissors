from django.urls import path

from game import views


urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('home/last=<int:last>', views.home, name='home'),
    path('create_game/<option>', views.create_game, name='create_game'),
    path('play_game', views.play_game, name='play_game'),
    path('continue_game/game=<int:game_id>', views.continue_game, name='continue_game'),
    path('see_moves/game=<int:game_id>/last=<int:last>', views.see_moves, name='see_moves'),
]