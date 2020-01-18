# Python Standard Library imports
import sys
import time
import math
import tkinter as tk


class Board(tk.Tk):

    def __init__(self, init_board, *args, **kwargs):

        # Initialize parent tk class
        tk.Tk.__init__(self, *args, **kwargs)

        self.tiles = {}
        self.board = init_board
        self.b_size = len(init_board)


class Tile():

    # Goal constants
    T_NONE = 0
    T_GREEN = 1
    T_RED = 2

    # Piece constants
    P_NONE = 0
    P_GREEN = 1
    P_RED = 2

    # Outline constants
    O_NONE = 0
    O_SELECT = 1
    O_MOVED = 2

    def __init__(self, tile=0, piece=0, outline=0, row=0, col=0):
        self.tile = tile
        self.piece = piece
        self.outline = outline

        self.row = row
        self.col = col
        self.loc = (row, col)

# main engine
class Halma():
    # init method
    def __init__(self):

        f = open("input.txt", "r")
        s = f.readlines()
        s = self.parse_input(s)
        f.close()

        self.game_type = s[0]  # eg - SINGLE

        self.b_size = 16
        self.t_limit = float(s[2]) * 1000 
        
        if s[1] == "BLACK":
            self.c_player = Tile.P_RED
            self.current_player = Tile.P_RED
        else:
            self.c_player = Tile.P_GREEN
            self.current_player = Tile.P_GREEN

        game_state = s[3:]

        board = [[None] * self.b_size for _ in range(self.b_size)]
        for row in range(self.b_size):
            for col in range(self.b_size):
                if game_state[row][col] == 'W':
                    board[row][col] = Tile(1, 1, 0, row, col)
                elif game_state[row][col] == 'B':
                    board[row][col] = Tile(2, 2, 0, row, col)
                else:
                    board[row][col] = Tile(0, 0, 0, row, col)

        # Create initial board

        self.r_camps = []
        self.g_camps = []
        for row in range(self.b_size):
            for col in range(self.b_size):
                if row + col < 6:
                    if row != 5 and col != 5:
                        element = Tile(2, 2, 0, row, col)
                        self.r_camps.append(element)
                elif row + col > 2 * (self.b_size - 4):
                    if row != self.b_size - 6 and col != self.b_size - 6:
                        element = Tile(1, 1, 0, row, col)
                        self.g_camps.append(element)

        self.board = board
        self.selected_tile = None
        self.valid_moves = []
        self.computing = False
        self.total_plies = 0

        self.ply_depth = 2
        # self.weight = [0.911, 0.140, 0.388] # depth = 2
        self.weight = [0.902, 0.004, 0.431] # depth = 4
        self.ab_enabled = True

        # if self.c_player == self.current_player:
        self.agent_move()

    # parse input file
    def parse_input(self, s):
        cnt = 0
        while (cnt <= 18):
            s[cnt] = s[cnt].strip("\n")
            cnt = cnt + 1
        return s

    # minimax & alpha-beta pruning
    def minimax(self, depth, player_to_max, max_time, a=float("-inf"),
                b=float("inf"), maxing=True, prunes=0, boards=0):

        # Bottomed out base case
        if depth == 0 or self.find_winner():
            return self.estimate(player_to_max), None, prunes, boards

        # Setup initial variables and find moves
        best_move = None
        if maxing:
            best_val = float("-inf")
            moves = self.get_next_moves(player_to_max)
        else:
            best_val = float("inf")
            moves = self.get_next_moves((Tile.P_RED
                                         if player_to_max == Tile.P_GREEN else Tile.P_GREEN))

        # For each move
        for move in moves:
            for to in move["to"]:

                # Bail out when we're out of time
                timeVal = time.time()

                if timeVal > max_time:
                    return best_val, best_move, prunes, boards

                # Move piece to the move outlined
                piece = move["from"].piece
                self.board[move["from"].row][move["from"].col].piece = Tile.P_NONE
                self.board[to.row][to.col].piece = piece
                boards += 1

                # Recursively call self
                val, _, new_prunes, new_boards = self.minimax(depth - 1,
                                                              player_to_max, max_time, a, b, not maxing, prunes, boards)

                prunes = new_prunes
                boards = new_boards

                # Move the piece back
                self.board[to.row][to.col].piece = Tile.P_NONE
                self.board[move["from"].row][move["from"].col].piece = piece

                if maxing and val > best_val:
                    best_val = val
                    best_move = (move["from"].loc, to.loc)
                    a = max(a, val)

                if not maxing and val < best_val:
                    best_val = val
                    best_move = (move["from"].loc, to.loc)
                    b = min(b, val)

                if self.ab_enabled and b <= a:
                    return best_val, best_move, prunes + 1, boards

        return best_val, best_move, prunes, boards
    # agent move
    def agent_move(self):

        # Print out search information
        current_turn = (self.total_plies // 2) + 1
        print("Turn", current_turn, "Computation")
        print("=================" + ("=" * len(str(current_turn))))
        print("Executing search ...", end=" ")
        # sys.stdout.flush()

        self.computing = True
        max_time = time.time() + self.t_limit

        # Execute minimax search
        _, move, prunes, boards = self.minimax(self.ply_depth,
            self.c_player, max_time)

        move_from = self.board[move[0][0]][move[0][1]]
        move_to = self.board[move[1][0]][move[1][1]]

        # forced code
        moves = self.get_moves_at_tile(move_from, self.c_player)
        index = moves.index(move_to)

        if abs(move_to.loc[0] - move_from.loc[0]) <= 2 and abs(move_to.loc[1] - move_from.loc[1]) <= 2:
            proc = "no changeable pick"  
        elif index == 1 or index == len(moves) - 1:
            print("4, 6")
            move_to = moves[index - 1]  
 
        ############
        print(move[0], move[1])
 
        lst = list(move)
        lst1 = list(lst[0])
        lst2 = list(lst[1])
        lst2[0] = move_to.loc[0]
        lst2[1] = move_to.loc[1]
        t1 = tuple(lst1)
        t2 = tuple(lst2)
        t = [t1, t2]
        move = tuple(t)
        print(move)
        output = ''
        if self.getAdjacentMovePath(move[0], move[1]) == True:
            output = 'E ' + str(move[0][1]) + ',' + str(move[0][0]) + ' ' + str(move[1][1]) + ',' + str(move[1][0]) + '\n'
            print(output)
        else:
            self.path = []
            self.getJumpMovePath(move[0], move[1])

            previous = ()

            for p in self.path:
                if len(previous) == 0:
                    previous = p
                    continue
                else:
                    output += "J " + str(previous[1])  + ',' + str(previous[0]) + ' ' + str(p[1]) + ',' + str(p[0]) + '\n'
                    previous = p
        
        f = open('output.txt', 'w')

        f.write(output)
        
        f.close()
        
        self.computing = False
    # adjacent move detection 
    def getAdjacentMovePath(self, fromPos, toPos):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if fromPos[0] + i == toPos[0] and fromPos[1] + j == toPos[1]:
                    return True
        return False
    # skip move detection
    def getJumpMovePath(self, fromPos, toPos):
        
        for i in range(-1, 2):
            for j in range(-1, 2):
                if fromPos[1] + j*2 == toPos[1] and fromPos[0] + i*2 == toPos[0]:
                    print("endpoint: ", self.path)
                    self.path.append(fromPos)
                    return self.path.append(toPos)

        for i in range(-1, 2):
            for j in range(-1, 2):

                if 0 <= fromPos[0] + i < self.b_size and 0 <= fromPos[1] + j < self.b_size and \
                    0 <= fromPos[0] + i*2 < self.b_size and 0 <= fromPos[1] + j*2 < self.b_size:
                    adjacent = self.board[fromPos[0] + i][fromPos[1] + j]
                    skip = self.board[fromPos[0] + i*2][fromPos[1] + j*2]

                    if i != 0 or j != 0:

                        if adjacent.tile != Tile.P_NONE and skip.tile == Tile.P_NONE:
                            
                            bEnd = False
                            for p in self.path:
                                if p[0] == fromPos[0] + i*2 and p[1] == fromPos[1] + j*2:
                                    bEnd = True
                                    break
                            if not bEnd:
                                self.path.append(fromPos)
                                return self.getJumpMovePath((fromPos[0] + i*2, fromPos[1] + j*2), toPos)

    # next move
    def get_next_moves(self, player=1):

        moves = []  # All possible moves
        for col in range(self.b_size):
            for row in range(self.b_size):

                curr_tile = self.board[row][col]

                # Skip board elements that are not the current player
                if curr_tile.piece != player:
                    continue

                move = {
                    "from": curr_tile,
                    "to": self.get_moves_at_tile(curr_tile, player)
                }
                moves.append(move)

        return moves
    # possible path search
    def get_moves_at_tile(self, tile, player, moves=None, adj=True):

        if moves is None:
            moves = []

        row = tile.loc[0]
        col = tile.loc[1]

        # List of valid tile types to move to
        valid_tiles = [Tile.T_NONE, Tile.T_GREEN, Tile.T_RED]
        if tile.tile != player:
            valid_tiles.remove(player)  # Moving back into your own goal
        if tile.tile != Tile.T_NONE and tile.tile != player:
            valid_tiles.remove(Tile.T_NONE)  # Moving out of the enemy's goal

        # Find and save immediately adjacent moves
        for col_delta in range(-1, 2):
            for row_delta in range(-1, 2):

                # Check adjacent tiles

                new_row = row + row_delta
                new_col = col + col_delta

                # Skip checking degenerate values
                if ((new_row == row and new_col == col) or
                    new_row < 0 or new_col < 0 or
                        new_row >= self.b_size or new_col >= self.b_size):
                    continue

                # Handle moves out of/in to goals
                new_tile = self.board[new_row][new_col]
                #if new_tile.tile not in valid_tiles:
                #continue

                if new_tile.piece == Tile.P_NONE:
                    if adj:  # Don't consider adjacent on subsequent calls
                        moves.append(new_tile)
                    continue

                # Check jump tiles

                new_row = new_row + row_delta
                new_col = new_col + col_delta

                # Skip checking degenerate values
                if (new_row < 0 or new_col < 0 or
                        new_row >= self.b_size or new_col >= self.b_size):
                    continue

                # Handle returning moves and moves out of/in to goals
                new_tile = self.board[new_row][new_col]
                #if new_tile in moves or (new_tile.tile not in valid_tiles):
                if new_tile in moves:
                    continue

                if new_tile.piece == Tile.P_NONE:
                    #moves.insert(0, new_tile)  # Prioritize jumps
                    moves.append(new_tile)
                    self.get_moves_at_tile(new_tile, player, moves, False)

                # camp rule
                if self.c_player == Tile.P_RED:
                    for r_move in moves:
                        for r_tile in self.r_camps:
                            if r_move.loc == r_tile.loc:
                                moves.remove(r_move)

                if self.c_player == Tile.P_GREEN:
                    for g_move in moves:
                        for g_tile in self.g_camps:
                            if g_move.loc == g_tile.loc:
                                moves.remove(g_move)
                
        return moves
    # game winner check
    def find_winner(self):

        if all(g.piece == Tile.P_GREEN for g in self.r_camps):
            return Tile.P_GREEN
        elif all(g.piece == Tile.P_RED for g in self.g_camps):
            return Tile.P_RED
        else:
            return None
    # evaluation function
    def estimate(self, player):

        greenVal = 0
        redVal = 0
        for col in range(self.b_size):
            for row in range(self.b_size):
                tile = self.board[row][col]
                if tile.piece == Tile.P_NONE:
                    continue
                if tile.piece == Tile.P_GREEN:

                    orientTileOffset = min(tile.loc[0], tile.loc[1])
                    orientTileLoc = [
                        tile.loc[0] - orientTileOffset, tile.loc[1] - orientTileOffset]
                    if orientTileLoc[0] > 4 or orientTileLoc[1] > 4:
                        orientTileLoc = (0, 0)

                    # + abs(tile.loc[0] - tile.loc[1])
                    greenVal += math.sqrt((orientTileLoc[0] - tile.loc[0])**2 + (
                        orientTileLoc[1] - tile.loc[1])**2)

                    deep = tile.loc[0] + tile.loc[1]
                    if deep == 30:
                        greenVal += 6
                    elif deep == 29:
                        greenVal += 5
                    elif deep == 28:
                        greenVal += 4
                    elif deep == 27:
                        greenVal += 3
                    elif deep == 26:
                        greenVal += 2
                    elif deep == 25:
                        greenVal += 1

                elif tile.piece == Tile.P_RED:

                    orientTileOffset = min(15 - tile.loc[0], 15 - tile.loc[1])
                    orientTileLoc = [
                        tile.loc[0] + orientTileOffset, tile.loc[1] + orientTileOffset]
                    if orientTileLoc[0] < 11 or orientTileLoc[1] < 11:
                         orientTileLoc = (15, 15)

                    # + abs(tile.loc[0] - tile.loc[1])
                    redVal += math.sqrt((orientTileLoc[0] - tile.loc[0])**2 + (
                        orientTileLoc[1] - tile.loc[1])**2)

                    deep = tile.loc[0] + tile.loc[1]
                    if deep == 0:
                        redVal += 6
                    elif deep == 1:
                        redVal += 5
                    elif deep == 2:
                        redVal += 4
                    elif deep == 3:
                        redVal += 3
                    elif deep == 4:
                        redVal += 2
                    elif deep == 5:
                        redVal += 1

        if(player == Tile.P_GREEN):
            return -greenVal
        else:
            return -redVal


if __name__ == "__main__":

    halma = Halma()
