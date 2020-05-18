#!/usr/bin/env python3
from game import Game
# from datetime import datetime
import sys, random, tty, os, termios
import argparse
from time import sleep

def play_console():
    global cursor,turn

    checkers.draw_board(cursor, turn)
    try:
        while True:
            k = getkey()
            if k == 'left':
                cursor = checkers.check_next_col_row(cursor, "left")
                checkers.draw_board(cursor, turn)

            elif k == 'right':
                cursor = checkers.check_next_col_row(cursor, "right")
                checkers.draw_board(cursor, turn)
            
            elif k == 'up':
                cursor = checkers.check_next_col_row(cursor, "up")
                checkers.draw_board(cursor, turn)

            elif k == 'down':
                cursor = checkers.check_next_col_row(cursor, "down")
                checkers.draw_board(cursor, turn)

            elif k == 'space':
                if checkers.previous:
                    valid = checkers.move_selected(cursor, turn)
                    if valid:
                        turn = -1 if turn == 1 else 1
                        checkers.change_turn(turn)
                        checkers.draw_board(cursor, turn)

                        if play_random:
                            checkers.play_random(turn)
                            turn = -1 if turn == 1 else 1
                            checkers.change_turn(turn)
                            checkers.draw_board(cursor, turn)
                else:
                    checkers.set_selected(cursor, turn)
                    checkers.draw_board(cursor, turn)

            elif k == 'backspace':
                if len(checkers.aval_moves) > 0:
                    checkers.remove_selected()
                    checkers.draw_board(cursor, turn)

    except (KeyboardInterrupt, SystemExit):
        os.system('stty sane')
        sys.exit()

def sim():
    global cursor,turn

    while True:
        checkers.play_random(turn)
        turn = -1 if turn == 1 else 1
        checkers.change_turn(turn)
        checkers.draw_board(cursor, turn)
        sleep(delay)

def getkey():
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        while True:
            b = os.read(sys.stdin.fileno(), 3).decode()
            if len(b) == 3: k = ord(b[2])
            else: k = ord(b)

            key_mapping = { 27:'esc', 32:'space', 68:'left', 67:'right', 66:'down', 65:'up', 127:'backspace' }
            return key_mapping.get(k, chr(k))

    except Exception: sys.exit()
    finally: termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    opt = ap._action_groups.pop()
    req = ap.add_argument_group('required arguments')
    opt.add_argument("-r","--random",action="store_true",help="play against random moves")
    opt.add_argument("-s","--sim",action="store_true",help="simulate random moves game")
    opt.add_argument("-d","--delay",type=float,help="delay between moves played in simulated game")
    opt.add_argument("-c","--color",const=1,type=int,choices=[42, 43, 44, 45, 46, 47],nargs="?",help="choose to select one color for the style of game, instead of random on load")
    opt.add_argument("-l","--log",action="store_true",help="disable logging of games to logs/ for highscore")
    opt.add_argument("-m","--moves",action="store_true",help="disable showing of available moves in game")
    ap._action_groups.append(opt)
    args = vars(ap.parse_args())

    mode, sep, play_random, color, delay, _sim = False, " ", False, 44, .15, False
    show_moves, next_random = 32, False
    cursor, turn = [7,0], random.choice([1, -1])
    match_colors = {43:33, 44:34, 45:35, 46:36, 47:37}
    if args["random"]: play_random = True
    if args["color"]: color = args["color"]
    if args["moves"]: show_moves = match_colors[color]
    if args["sim"]: delay, _sim = 0, True
    if args["delay"]: delay = args["delay"]

    checkers = Game(mode=mode, starter=turn, color=color, show=show_moves, delay=delay)
    if _sim: sim()
    else: play_console()