# Intrigue
This program simulates a game of Intrigue based on the board game (https://boardgamegeek.com/boardgame/265/intrigue).<br>
<br>
The goal of the game is to end the 6th round as the richest Player. Each turn Players send their Pieces to other Players to get a job. Each Piece that gets a job collects a salary each turn. Each Player owns a palace with four jobs, so they must accept 4 pieces for these jobs. However, when multiple pieces apply for the same position, or more pieces apply than there are jobs, the Player chooses which pieces to reject, removing them from the game.

## How to Run
To execute, run the following in the command console, choosing a player type out of the existing ones:<br>
`python path_to_intrigue.py [player_type_classname] [player_type_classname] [player_type_classname] [player_type_classname]`<br>
Example:<br>
`python intrigue.py PlayerRandom PlayerHonest PlayerHuman PlayerHonest`

## Game Structure
The game is currently implemented for four players, each a different colour, where each player owns:<br>

- A palace with 4 Squares.<br>
- 8 Pieces of their colour.<br>
- 32000 Ducats (currency).<br>

The existing Classes are as follows:

### Square
| Attributes| Description |
| ----------- | ----------- |
| piece:Piece | The piece contained in the Square. |
| value:int | The value of this Square, for salary collection. |
| owner:Player | This Square's owner. |

### Piece
| Attributes| Description |
| ----------- | ----------- |
| owner:Player | This Piece's owner. |
| type:Piece_Type | The type of Piece this is. The available Player_Types are: SCIENTIST, DOCTOR, CLERK, PRIEST |

### Application
| Attributes| Description |
| ----------- | ----------- |
| None | An Application is a tuple of (Piece,Square). Each Player sends Applications to other Players, indicating they'll send them the given Piece and that they want it to be placed at the given Square.  |

### Player
| Attributes| Description |
| ----------- | ----------- |
| pieces:list[Piece] | The list of Pieces in the player's hand. |
| money:int | The amount of ducats the player has available for bribing. |
| colour:Player_Colour | The type of colour this is. The available Player_Colour are: RED, GREEN, BLUE, YELLOW |
| palace_applicants:list[Application] | The Applications sent to this Player, for them to accept or reject. |
| history_applications:list[(Application,Player)] | The Applications this Player has sent and who they've been sent to. |

### Game
| Attributes| Description |
| ----------- | ----------- |
| players:list[Player] | The game's players. |
| board:list[list[Square]]| The gameboard. A list where each row represents a Player's Squares. Each row corresponds to the Player with the Player_Colour.value as its index. |

## How to Play
The game progresses in turns, which are indicated in the console. Each Turn has the following phases:
#### Send Pieces
The Player picks one of their Pieces and sends them to another Player's palace to get a job. If there are no other Pieces of the same type applying for the Palace, then the Piece must be accepted.<br>
This is done twice, sending two pieces each turn at the end of their turn until there are none left.
#### Collect Salaries
All of the Player's Pieces currently in a Square collect the salary corresponding to that Square's value.
#### Resolve Conflicts
The Player must deal with the Applications they themselves received from the other Players:<br>

1. If the Player received multiple Applications from the same type of Piece (ex. PRIEST), then the Player must pick one to pick, rejecting the others.<br>
2. If the Player received an Application for a type of Piece that already has a Square, then the Player must choose whether to keep that Piece or replace it with the new one.<br>
3. Otherwise, the Application does not have a conflict, and must simply be placed in a Square of the Player's choosing.<br>

During 1, 2 and 3, the Player asks the owners of the Pieces to give them a bribe (minimum of 1000). This process is public and a Player is not bound by any deals made at this point. If a RED PRIEST and a BLUE PRIEST are competing for a job, and the BLUE owner bribes for 8000 whereas the RED owner bribes 1000, the Player may choose to reject BLUE and keep RED.

## Player Types
Player types are specific instances of the abstract class Player, extending it and implementing the following functions:
| Function | Description |
| ----------- | ----------- |
| play_piece(self, board, players) -> tuple[Application,Player] | Function that, looking at the game board and each of the Players, decides which player to send an Application to. |
| select_square_to_place(self, board, players, application, bribes) -> Square | Given an Application and the bribes received from each Application, decides in which Square to place this Application's Piece. |
| resolve_external_conflict(self, board, players, bribes) -> Application | Given the list of Pieces and corresponding bribes, chooses one to keep, rejecting the others. |
| resolve_internal_conflict(self, board, players, board_square, bribes) -> Piece | Given the two Pieces and corresponding bribes, chooses one to keep in the Square, rejecting the other. |
| decide_bribe(self, application, previous_bribes) -> int | The Player decides how much of a bribe they are willing to pay for their Application. previous_bribes represents the bribes other players have already given to compete with yours (it may be the case that some or none of the other players have given their bribe yet). |

To create a new Player Type, Player must be extended, and the above functions must be implemented.<br>
`class newPlayerTypeName(Player):`

### Available Player Types
**PlayerHuman**
: A human player who asks the reader to input the next action in the console as prompted.

**PlayerRandom**
: A random player who chooses randomly what to do out of their possible action space.

**PlayerHonest**
: An honest player who always acts fairly, accepting the Pieces with the highest bribe and sending Applications for the highest paying jobs. The attempt to bribe fairly for each position, aiming to be the highest paying briber.

## TODO
- General debugging for each Behaviour.
- Log all actions in the system. Currently, only Applications sent to others are logged.
- Create mental models for each Player to interpret other Player's actions to use in their decisions.
- Create reaction functions. Each Player should have functions for reacting to other player moves and updating their mental models.
