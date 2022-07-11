wins_dict:dict = {}
"""Dictionary that given a move, returns the number of times that move's simulation results in a win."""

sims_dict:dict = {}
"""Dictionary that given a move, returns the number of times that move has been simulated."""

def get_play(states, time_limit):
    """Given the states so far, returns the best move for the current state."""
    global wins_dict, sims_dict  

    state = states[-1]
    player = current_player(state)
    possible_moves = legal_plays(state)

    # Bail out early if there is no real choice to be made.
    if not possible_moves:
        return
    if len(possible_moves) == 1:
        return possible_moves[0]

    n_games = 0
    begin = datetime.datetime.utcnow()
    while datetime.datetime.utcnow() - begin < time_limit:
        wins_dict, sims_dict = run_simulation(state)
        n_games += 1

    #Get move with best win/sim ratio.
    chosen_move = max([wins_dict[move] / sims_dict[move] for move in possible_moves])

    return chosen_move

def run_simulation(root_state):
    """Plays out a "random" game from the current position, then updates the statistics tables with the result."""
    global wins_dict, sims_dict     

    #Root node of the tree.
    current_state = root_state
    #States visited in this simulation run. Represents the branch of the tree for this simulation run.
    visited_states = []

    expand = True
    for _ in range(20):      
        possible_moves = legal_plays(current_state)        
        #List of move and state that move results in. This represents all children of current tree node.
        moves_states = [(play, next_state(current_state, play)) for play in possible_moves]

        #Checks if all states for current tree node have been simulated at least once.
        for move, state in moves_states:
            already_recorded = sims_dict[state]
            if not already_recorded:
                break
        #If all states have been simulated at least once, apply UCT to decide next move.
        if already_recorded:
            sum = 0
            for move, state in moves_states:
                sum += sims_dict[state]
            log_total = math.log( sum )
            uct_value, chosen_move, current_state = max( ((wins_dict[state] / sims_dict[state]) + self.C * sqrt(log_total / sims_dict[state]), move, state)
                for move, state in moves_states)
                #Consider the max function to return the tuple with the maximum uct_value. (self.C refers to the UCT constant.)
        else:
            chosen_move, current_state = random.choice(moves_states)

        #If this play hasn't been expanded, expand it. (Set stats to default 0)
        if expand and current_state not in sims_dict.keys():
            expand = False
            sims_dict[current_state] = 0
            wins_dict[current_state] = 0

        visited_states.append(current_state)

        winner_int = winner(current_state)
        if winner_int >= 0:  #Game has finished.
            break

    #Update stats for expanded plays. (Only expanded are in dictionary.)
    for state in visited_states:
        if state in sims_dict.keys():
            sims_dict[state] += 1
            #If this montecarlo player is the winner at the end of the simulation, increase dictionary value for wins.
            if current_player(root_state) == winner(state):
                wins_dict[state] += 1

def next_state(state, play):
    """Returns a new state, applying play to given state."""

def current_player(state) -> int:
    """Returns the numeric value for the current player for the given state."""

def legal_plays(state):
    """Returns the possible moves for the given state."""

def winner(state) -> int:
    """Returns the numeric value of the winner for the given state, or -1 if the game has not finished.."""