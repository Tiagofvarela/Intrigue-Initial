from random import randint
from intrigueAI import IntrigueAI
from intrigue_datatypes import MINIMUM_BRIBE, Player_Colour


class RandomAI(IntrigueAI):
    """Makes random decisions."""

    def get_play(self):
        """Returns a play for the current state. (Default: Random)\nUpdates log accordingly."""
        file = open(self.filename,"a")
        file.write(repr(self.states[-1])+"\n")
        chosen_play = self.board.get_random_legal_play(self.states, self.decide_bribe)
        log_info = "Round:"+str(self.states[-1].turn_counter+1)+" "+Player_Colour(self.states[-1].get_player_turn()).clean_name()+" Turn\n"+"Random play chosen: \n"+repr(chosen_play)+"\n"
        print(log_info)
        file.write(log_info)
        file.close()
        return chosen_play

    def decide_bribe(self, piece, square, max_spendable=None) -> int:
        """Decide bribe to give to player so they accept the application. 
        \nAmount is subtracted from account."""
        state = self.get_current_state()

        #Bribe is set to random value between min and a fourth of total.
        bribe = randint(MINIMUM_BRIBE, max(round( state.players[state.get_player_turn()].money /4),MINIMUM_BRIBE) )
        #self.money -= bribe
        return bribe