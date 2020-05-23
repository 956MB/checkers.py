# -*- coding: utf-8 -*- 
from __future__ import print_function
import numpy as np
import os, csv, sys, random, time
# from timer import Timer

# I think plenty of things in here can be redone to be a bit simpler and more streamlined, but it all pretty much works atm, and that was the initial goal. Overall, it's a pretty good start. It is Python, after all.
# Comments should probably be put in eventually as a well. It gets a bit confusing in parts.

class Game(object):
    def __init__(self, mode=True, starter=1, color=44, show=32, delay=0, show_extra=False):
        self.delay, self.starting_color, self.show_extra = delay, starter, show_extra
        self.moves, self.aval_moves, self.current_move, self.current_turn = [[]], [], [], starter
        self.red_score, self.black_score, self.red_moves, self.black_moves, self.red_kings, self.black_kings = 0, 0, 0, 0, 0, 0
        self.previous, self.color, self.show_moves = [], color, show
        self.swap, self.winner = True, False
        self.board = self.populate_board()

        if self.color in [43, 47]: self.cursor_color = 90
        else: self.cursor_color = 37
        if self.color == 42: self.show_moves = 94
        self.turn_color = 31 if self.current_turn == 1 else 30

        self.pieces = { 0:" {} \033[0m", 1:"\033[91m {} \033[0m", -1:"\033[30m {} \033[0m", 2:" {} \033[0m", 3:"\033[{}m {} \033[0m", 4:"\033[{}m {} \033[0m", 5:"\033[91m {} \033[0m", 6:"\033[30m {} \033[0m" }
        self.turns = {1:"\033[{}m\033[91m ● \033[0m", -1:"\033[{}m\033[30m ● \033[0m"}
        # self.types = {0:"BLANK", 1:"RED", -1:"BLACK", 2:"SPACE", 3:"SELECTED", 4:"AVAILABLE", 5:"RED_KING", 6:"BLACK_KING"}

    def populate_board(self):
        flat = [0]*64
        if self.current_turn == 1: black, red, extra = [1, 3, 5, 7, 8, 10, 12, 14, 17, 19, 21, 23], [40, 42, 44, 46, 49, 51, 53, 55, 56, 58, 60, 62], [24, 26, 28, 30, 33, 35, 37, 39]
        elif self.current_turn == -1: red, black, extra = [1, 3, 5, 7, 8, 10, 12, 14, 17, 19, 21, 23], [40, 42, 44, 46, 49, 51, 53, 55, 56, 58, 60, 62], [24, 26, 28, 30, 33, 35, 37, 39]

        for i,v in enumerate(flat):
            if i in black: flat[i] = -1
            elif i in red: flat[i] = 1
            elif i in extra: flat[i] = 2
            else: flat[i] = 0

        return np.reshape(flat, (8,8))

    def play_random(self, piece):
        random_move = random.choice(self.get_available_pieces(piece))
        node, self.aval_moves = random_move[0], [random.choice(random_move[1])]
        
        self.xtest, self.ytest, move_r, move_c = node[0], node[1], self.aval_moves[0][-1][0], self.aval_moves[0][-1][1]
        self.previous = self.board[self.xtest][self.ytest]
        self.current_move.append([self.xtest, self.ytest])

        self.board[move_r][move_c] = 4
        self.move_selected([move_r, move_c], self.current_turn)

    def get_available_pieces(self, piece):
        pieces = []
        turn = [1, 5] if piece == 1 else [-1, 6]
        for row_idx, row in enumerate(self.board):
            for col_idx, item in enumerate(row):
                if item in turn:
                    moves = self.get_available_moves([row_idx, col_idx])
                    if len(moves) > 0: pieces.append([[row_idx, col_idx], moves])
                    self.remove_available_moves()
                    
        return pieces

    def reset_game(self, new_turn):
        self.board = self.populate_board()
        self.moves, self.red_score, self.black_score = [], 0, 0
        # self.starter = new_turn
    
    def change_turn(self, turn):
        self.current_turn = turn
        self.turn_color = 31 if turn == 1 else 30
        self.swap = False if self.swap else True

    def set_selected(self, picked, turn):
        self.xtest, self.ytest = picked[0], picked[1]
        turn = [1, 5] if turn == 1 else [-1, 6]
        if self.board[self.xtest][self.ytest] in turn:
            self.aval_moves = self.get_available_moves([self.xtest, self.ytest])
            if len(self.aval_moves) > 0:
                self.previous = self.board[self.xtest][self.ytest]
                self.current_move.append([self.xtest, self.ytest])
                self.board[self.xtest][self.ytest] = 3

    def remove_selected(self):
        self.board[self.xtest][self.ytest] = self.previous
        self.previous, self.current_move = [], []
        self.remove_available_moves()

    def move_selected(self, spot, turn):
        if self.valid_placement(spot):
            newx, newy = spot[0], spot[1]
            self.current_cursor = newx, newy
            # self.board[self.xtest][self.ytest] = 2
            self.push_move([newx, newy])
            return True
        else:
            return False

    def push_move(self, new_spot):
        self.current_move.append(new_spot)
        self.current_move.append(self.previous)
        self.moves.append(self.current_move)
        self.loop_moves(new_spot)
        self.remove_available_moves()
        self.previous, self.current_move = [], []

    def remove_available_moves(self):
        flat_board, self.aval_moves = [2 if x==4 else x for x in self.board.flatten()], []
        self.board = np.reshape(flat_board, (8,8))

    def loop_moves(self, landing):
        start_node, moves, end = self.current_move[0], self.aval_moves, landing
        moves = [i for i in self.aval_moves if end in i and i[-1] == end][-1]
        for move in moves:
            self.capture_piece(start_node, move)
            start_node = move
            self.draw_board(self.current_cursor, self.change_turn)

    def capture_piece(self, start, end):
        start_r, start_c, end_r, end_c, jumped_pieces = start[0], start[1], end[0], end[1], []
        _, left_right, opponent = self.return_meta([end_c, start_c])
        opponent = [1, 5] if opponent == 1 else [-1, 6]
        up_down = "+" if start_r < end_r else "-"

        for i in range(1, abs(start_r-end_r)):
            p_r, p_c = eval("start_r%si" % up_down), eval("start_c%si" % left_right)
            if self.board[p_r][p_c] in opponent: jumped_pieces.append([p_r, p_c])
        
        if len(jumped_pieces) > 0:
            for i in jumped_pieces:
                self.board[i[0]][i[1]] = 2
                self.increase_score()
                self.increase_moves()
                self.check_winner()
        else:
            self.increase_moves()

        self.board[start_r][start_c] = 2
        self.king_piece(start_r, start_c, end_r, end_c)
        time.sleep(self.delay)

    def valid_placement(self, cursor):
        return True if self.board[cursor[0]][cursor[1]] == 4 else False
    
    def check_winner(self):
        if self.red_score == 12: self.winner = 1
        elif self.black_score == 12: self.winner = -1

    def return_meta(self, ec_sc=None, king=False):
        left_right = None
        up_down = ["-"] if self.swap else ["+"]
        if ec_sc: left_right = "-" if ec_sc[0] < ec_sc[1] else "+"
        opponent = -1 if self.current_turn == 1 else 1
        if king: up_down = ["-", "+"]

        return up_down, left_right, opponent

    def check_next_col_row(self, cursor, direction):
        if direction == "right": cursor[1] = 0 if cursor[1] == 7 else cursor[1]+1
        elif direction == "left": cursor[1] = 7 if cursor[1] == 0 else cursor[1]-1
        elif direction == "up": cursor[0] = 7 if cursor[0] == 0 else cursor[0]-1
        elif direction == "down": cursor[0] = 0 if cursor[0] == 7 else cursor[0]+1
        return cursor
    
    def get_available_moves(self, selected):
        # Yes, this function is incredibly long winded. I sort of got carried away with making it work in the moment and wasnt thinking about the best way to do it. This can probably be rewritten.
        if self.board[selected[0]][selected[1]] in [5,6]: if_king = True
        else: if_king = False
        up_down, _, opponent = self.return_meta(king=if_king)
        available_moves, paths = [], []

        # \ /
        for up_down_sign in up_down:
            for sign in ["-", "+"]:
                opposite_sign = "-" if sign == "+" else "+"
                row, col, skip = selected[0], selected[1], False
                skip_opp = False
                for _ in range(0, 7):
                    row = eval("row%s1" % (up_down_sign))
                    col = eval("col%s1" % (sign))
                    if self.check_bounds(row, col): break
                    if skip:
                        skip = False
                        continue
                    if self.board[row][col] == 2 and 0 <= col <= 7:
                        available_moves.append([[row, col]])
                        self.board[row][col] = 4
                        break
                    elif self.board[row][col] == self.current_turn: break
                    elif self.board[row][col] == opponent:
                        new_row, new_col = eval("row%s1" % (up_down_sign)), eval("col%s1" % (sign))
                        if self.check_bounds(new_row, new_col): break
                        if self.board[new_row][new_col] == 2:
                            available_moves.append([[new_row, new_col]])
                            paths.append([new_row, new_col])
                            self.board[new_row][new_col] = 4

                            # Check opposite angle path:
                            new_row_copy, new_col_copy = new_row, new_col
                            for _ in range(1, 7):
                                if skip_opp:
                                    skip_opp = False
                                    continue
                                opp_row, opp_col = eval("new_row_copy%s1" % (up_down_sign)), eval("new_col_copy%s1" % (opposite_sign))
                                if self.check_bounds(opp_row, opp_col): break
                                if self.board[opp_row][opp_col] == opponent:
                                    next_opp_row, next_opp_col = eval("opp_row%s1" % (up_down_sign)), eval("opp_col%s1" % (opposite_sign))
                                    if self.check_bounds(next_opp_row, next_opp_col): break
                                    if self.board[next_opp_row][next_opp_col] == 2:
                                        paths.append([next_opp_row, next_opp_col])
                                        self.board[next_opp_row][next_opp_col] = 4
                                        new_row_copy, new_col_copy = next_opp_row, next_opp_col
                                        if self.check_bounds(new_row_copy, new_row_copy): break
                                    else:
                                        skip_opp = True

                            available_moves.append(paths)
                            skip, paths = True, paths[:-1]
                            next_row, next_col = eval("new_row%s1" % (up_down_sign)), eval("new_col%s1" % (sign))
                            if self.check_bounds(next_row, next_col): break
                            if self.board[next_row][next_col] == 2: break
                        elif self.board[new_row][new_col] == opponent: break

        return available_moves

    def check_bounds(self, bound1, bound2):
        return True if bound1 in [-1,8] or bound2 in [-1, 8] else False

    def increase_score(self):
        if self.current_turn == 1: self.red_score += 1
        elif self.current_turn == -1: self.black_score += 1

    def increase_moves(self):
        if self.current_turn == 1: self.red_moves += 1
        elif self.current_turn == -1: self.black_moves += 1

    def king_piece(self, start_r, start_c, end_r, end_c):
        # Very annoying and long
        if self.starting_color == 1:
            if self.current_turn == 1 and end_r == 0:
                self.board[end_r][end_c] = 5
                if self.board[start_r][start_c] != 5: self.red_kings += 1
            elif self.current_turn == -1 and end_r == 7:
                self.board[end_r][end_c] = 6
                if self.board[start_r][start_c] != 6: self.black_kings += 1
            else: self.board[end_r][end_c] = self.previous
        elif self.starting_color == -1:
            if self.current_turn == -1 and end_r == 0:
                self.board[end_r][end_c] = 6
                if self.board[start_r][start_c] != 6: self.black_kings += 1
            elif self.current_turn == 1 and end_r == 7:
                self.board[end_r][end_c] = 5
                if self.board[start_r][start_c] != 5: self.red_kings += 1
            else: self.board[end_r][end_c] = self.previous

    def draw_board(self, cursor=[5,0], turn=1, winning_pieces=None):
        os.system('clear')
        if not self.winner: print("\n RED: {} | BLACK: {}\n".format(self.red_score, self.black_score))
        else: print()

        for row_index, row in enumerate(self.board):
            print(" ", end="")
            for col_index, item in enumerate(row):
                current = [row_index, col_index]
                
                if current == cursor:
                    if item == 1: print("\033[{}m{}".format(self.color, self.pieces[1].format("○")), end="")
                    elif item == -1: print("\033[{}m{}".format(self.color, self.pieces[-1].format("○")), end="")
                    elif item == 2: print("\033[{}m\033[{}m{}".format(self.color, self.cursor_color, self.pieces[2].format("○")), end="")
                    elif item == 3: print("\033[{}m{}".format(self.color, self.pieces[3].format(self.cursor_color, "○")), end="")
                    elif item == 4: print("\033[{}m\033[{}m{}".format(self.color, self.turn_color, self.pieces[4].format(self.turn_color, "○")), end="")
                    elif item == 5: print("\033[{}m{}".format(self.color, self.pieces[5].format("○")), end="")
                    elif item == 6: print("\033[{}m{}".format(self.color, self.pieces[6].format("○")), end="")
                    else: print("\033[40m\033[{}m{}".format(self.cursor_color, self.pieces[0].format("○")), end="")
                else:
                    if item == 1: print("\033[{}m{}".format(self.color, self.pieces[1].format("●")), end="")
                    elif item == -1: print("\033[{}m{}".format(self.color, self.pieces[-1].format("●")), end="")
                    elif item == 2: print("\033[{}m\033[30m{}".format(self.color, self.pieces[2].format(" ")), end="")
                    elif item == 3: print("\033[{}m{}".format(self.color, self.pieces[3].format(self.cursor_color, "○")), end="")
                    elif item == 4: print("\033[{}m\033[{}m{}".format(self.color, self.cursor_color, self.pieces[4].format(self.show_moves, "○")), end="")
                    elif item == 5: print("\033[{}m{}".format(self.color, self.pieces[5].format("✪")), end="")
                    elif item == 6: print("\033[{}m{}".format(self.color, self.pieces[6].format("✪")), end="")
                    else: print("\033[40m{}".format(self.pieces[0].format(" ")), end="")
            print()

        if not self.winner:
            print("\n TURN: {}".format(self.turns[self.current_turn].format(self.color)))
            # print(" LAST: {}".format(self.moves[-1]))
            print("\n ⭠ ⭡⭣ ⭢  to move.\n SPACE to select.\n BACKSPACE to deselect.\n CTRL+C to exit.\n")
        else:
            self.remove_available_moves()
            print("\n       WINNER: {}\n".format(self.turns[self.winner].format(self.color)))
            if self.show_extra:
                print(" -----SCORE-----")
                print(" RED: {}, BLACK: {}".format(self.red_score, self.black_score))
                print("\n -----MOVES-----")
                print(" TOTAL: {}\n RED: {}, BLACK: {}".format(len(self.moves), self.red_moves, self.black_moves))
                print("\n -----KINGS-----")
                print(" RED: {}, BLACK: {}\n".format(self.red_kings, self.black_kings))
            sys.exit()