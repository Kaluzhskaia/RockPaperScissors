from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# model to store the state of the whole game itself
class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    player1_name = models.CharField(max_length=30)
    player2_name = models.CharField(max_length=30)
    player1_score = models.PositiveIntegerField(default=0)
    player2_score = models.PositiveIntegerField(default=0)
    with_computer = models.BooleanField(default=False)

    # method for representation of current scores for players
    def __str__(self):
        return "%s (%s) vs %s (%s)" % (self.player1_name, self.player1_score, self.player2_name, self.player2_score)


# model to store the state of each separate move players make
class Move(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # cascade deleting all the moves if a game instance is deleted
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    # this will be rock/paper/scissors/tie
    player1_choice = models.CharField(max_length=8)
    player2_choice = models.CharField(max_length=8)
    winner = models.CharField(max_length=30)


# updating the game scores when a new move is made
@receiver(post_save, sender=Move)
def handle_new_job(sender, instance, created, **kwargs):
    if created:
        if not instance.winner == "Tie":
            if instance.winner == instance.game.player1_name:
                instance.game.player1_score += 1
            else:
                instance.game.player2_score += 1
        instance.game.save()
