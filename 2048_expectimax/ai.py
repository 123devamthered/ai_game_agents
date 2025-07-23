from __future__ import absolute_import, division, print_function
import copy, random
from game import Game

MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}
MAX_PLAYER, CHANCE_PLAYER = 0, 1 

# Tree node. To be used to construct a game tree. 
class Node: 
    # Recommended: do not modify this __init__ function
    def __init__(self, state, player_type):
        self.state = (state[0], state[1])

        # to store a list of (direction, node) tuples
        self.children = []

        self.player_type = player_type

    # returns whether this is a terminal state (i.e., no children)
    def is_terminal(self):
        #TODO: complete this
        if self.children == []:
            return True
        else:
            return False

# AI agent. Determine the next move.
class AI:
    # Recommended: do not modify this __init__ function
    def __init__(self, root_state, search_depth=3): 
        self.root = Node(root_state, MAX_PLAYER)
        self.search_depth = search_depth
        self.simulator = Game(*root_state)

    # (Hint) Useful functions: 
    # self.simulator.current_state, self.simulator.set_state, self.simulator.move

    # TODO: build a game tree from the current node up to the given depth

    def build_tree(self, node=None, depth=0):
        if node is None:
            node = self.root
            
        if depth > 0:

            self.simulator.set_state(*node.state)

            if node.player_type == MAX_PLAYER:
                for direction in range(4):
                    prev = self.simulator.current_state()
                    if self.simulator.move(direction):
                        succesor = self.simulator.current_state()
                        child_node = Node(succesor, CHANCE_PLAYER)
                        node.children.append((direction, child_node))
                        self.build_tree(child_node, depth - 1)
                        self.simulator.set_state(*prev)

            elif node.player_type == CHANCE_PLAYER:
                tile_matrix, score = node.state
                for x in range(4):
                    for y in range(4):
                        if tile_matrix[x][y] == 0:
                            new = copy.deepcopy(tile_matrix)
                            new[x][y] = 2  
                            child_state = (new, score)
                            child_node = Node(child_state, MAX_PLAYER)
                            node.children.append(((x, y), child_node))
                            self.build_tree(child_node, depth - 1)


    # TODO: expectimax calculation.
    # Return a (best direction, expectimax value) tuple if node is a MAX_PLAYER
    # Return a (None, expectimax value) tuple if node is a CHANCE_PLAYER
    def expectimax(self, node = None):
        # TODO: delete this random choice but make sure the return type of the function is the same
        if node.is_terminal() == True:
            return None, node.state[1]
        elif node.player_type == MAX_PLAYER:
            value = -10000000
            dir = -100000000
            for (direction,n) in node.children:
                new = self.expectimax(n)[1]
                if value < new:
                    value = new
                    dir = direction
            return dir, value
        elif node.player_type == CHANCE_PLAYER:
            value = 0
            for (direction,n) in node.children:
                value = value + self.expectimax(n)[1] * (1/len(node.children))
            return None, value

    # Return decision at the root
    def compute_decision(self):
        self.build_tree(self.root, self.search_depth)
        direction, _ = self.expectimax(self.root)
        return direction

    def heuristic(self, node):
        h_value = 0
        best = 0
    #     next_best = 0
    #     third_best = 0
        board = node.state[0]
        # in_order = 0
        my_list = []
        for row in range(len(board)-1):
            for col in range(len(board[0])-1):
                my_list.append(board[row][col])
                # board[row][col + 1] <= board[row][col]
                # in_order += 1
        my_list = sorted(my_list, reverse = True)
        best, next_best, third_best = my_list[0], my_list[1], my_list[2]
        top_row = 0
        if board[0][0] == best:
            top_row += 1
    #     if board[0][1] == next_best:
    #         top_row += 1
    #     if board[0][2] == third_best:
    #         top_row += 1
        s_value = 0
        simulation = Game(*node.state)
        if simulation.can_move():
            s_value += 2048 
        h_value = node.state[1] * best + s_value
        if board[0][0] == best:
            h_value *= 1.5
        
        # h_value += 0.5 * top_row * s_value # 0.3 * in_order + 
        return h_value

    # def heuristic(self, node):
    #     h_value = 0
    #     board = node.state[0]
    #     score = node.state[1]

    #     in_order = 0
    #     my_list = []

    #     for row in range(len(board)):
    #         for col in range(len(board[0])):
    #             my_list.append(board[row][col])
    #             if col < len(board[0]) - 1:  # Check within row bounds
    #                 if board[row][col + 1] <= board[row][col]:
    #                     in_order += 1

    #     my_list = sorted(my_list, reverse=True)
    #     best = my_list[0] if len(my_list) > 0 else 0
    #     next_best = my_list[1] if len(my_list) > 1 else 0
    #     third_best = my_list[2] if len(my_list) > 2 else 0

    #     top_row = 0
    #     for col in range(len(board[0])):
    #         if board[0][col] in (best, next_best, third_best):
    #             top_row += 1

    #     # Adjusted weights: less weight to top_row
    #     h_value = (0.5 * in_order) + (0.4 * score) + (0.4 * best) + (0.2 * top_row)
        
    #     return h_value


    def expectimax_ec(self, node = None):
        # TODO: delete this random choice but make sure the return type of the function is the same
        if node.is_terminal() == True:
            return None, self.heuristic(node)
        elif node.player_type == MAX_PLAYER:
            value = -10000000
            dir = -100000000
            for (direction,n) in node.children:
                new = self.expectimax_ec(n)[1]
                if value < new and direction != 2:
                    value = new
                    dir = direction
            if dir == -100000000:
                dir,n = node.children[0]
                value = self.expectimax_ec(n)[1]
            return dir, value
        elif node.player_type == CHANCE_PLAYER:
            value = 0
            for (direction,n) in node.children:
                value = value + self.expectimax_ec(n)[1] * (1/len(node.children))
            return None, value

    # TODO (optional): implement method for extra credits
    def compute_decision_ec(self):
        self.build_tree(self.root, 4)
        direction, _ = self.expectimax_ec(self.root)
        return direction


