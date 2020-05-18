# NOTE: Options: 
#       ● ○ ✪ ⦻ ⦾ ⦿ ⨂ ⦲ ◍

# NOTE: Color options:
#       Orange/Yellow: 43m, Blue: 44m, Purple/Pink: 45m, Cyan: 46m, Lightgrey: 47m

# TODO: General todos:
#       X Dont allow placement of pieces in opponent
#       X Provide turn to set, remove, select functions to play both sides
#       X Write 'check_move' function to check if valid move
#       X 'valid_moves' function(s) | also: dont allow backward movement until kinged.
#           X kinged? how? idk
#       X Figure out angled jumps (two or more opponent pieces not in straight line):
#       X Function that detects "cross overs", basically the scoring of jumping over enemy piece(s)
#       X Down the line: theming? color options based on args?
#       X Random color on launch, arg to disable random and select main color
#       - Keep logs/ of games for highscore stuff
#       - Add time
#       X Arg to show moves/disable show moves (toggle the green available move circle)
#       X Arg to start at either red or black piece
#       X Add arg 'play_random' to play random moves
#       X Add last move displayed for debugging
#       X Add winner check

# NOTE: Playing random moves SORT OF works atm. Sometimes the random move will block a capture, but then the available moves will dwindle. It can eventually block all paths and run out of moves. Sort of avoidable if you play aggressive and force it to move down the board. Not perfect OFC!

# BUG: Bugs:
#       maybe fixed? get_available_moves: allowing capture of two opponent pieces back to back, not expected behavior
#       X random moves seem to favor left side of board maybe??
#       maybe fixed? sometimes opponent can skip two blank spaces when going down "-"
#       X Black pieces are not being kinged for some reason. i see why right now, im loking at it

#       X Bug with cross paths: if you click move in the middle of a cross, it will select the two piece move instead of the one piece move you selected (i guess kind of a good thing, sine it doesnt allow you to miss two points, but still, it should allow you to make the move you want, if you miss it, its your fault.)
#       - Sometimes when simulating game, an indexerror will be raised because there are no available moves, which is wrong. I dont know why or which piece, but looking at the board, theres definetly options for pieces to move. - scratch that, its probably because of the random moves. sometimes it can randomly pick the worst moves and get the board stuck where no piece can move. BUT, sometimes it looks like theres plenty of open space more moves to be made, but it doesnt, i don know dude. Also, sometimes a game will end saying one player has 12 score, but there are still enemy piece on the board, i dont know why.