'''

    2020 CAB320 Sokoban assignment


The functions and classes defined in this module will be called by a marker script.
You should complete the functions and classes according to their specified interfaces.
No partial marks will be awarded for functions that do not meet the specifications
of the interfaces.


You are NOT allowed to change the defined interfaces.
That is, changing the formal parameters of a function will break the
interface and results in a fail for the test of your code.
This is not negotiable!


'''

# You have to make sure that your code works with
# the files provided (search.py and sokoban.py) as your code will be tested
# with these files
import search
import sokoban

#CHECK TO SEE IF THIS IS ALLOWED BEFORE SUBMITTING (ADDED BY CALISE)
from copy import deepcopy
import time

from itertools import *


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def my_team():
    '''
    Return the list of the team members of this assignment submission as a list
    of triplet of the form (student_number, first_name, last_name)

    '''
    return [(10469290, 'Emily', 'Guan'), (10084983, 'Danial', 'Baharvand'), (10489690, 'Calise', 'Newton')]
    # raise NotImplementedError()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def taboo_cells(warehouse):
    '''
    Identify the taboo cells of a warehouse. A cell inside a warehouse is
    called 'taboo'  if whenever a box get pushed on such a cell then the puzzle
    becomes unsolvable. Cells outside the warehouse should not be tagged as taboo.
    When determining the taboo cells, you must ignore all the existing boxes,
    only consider the walls and the target  cells.
    Use only the following two rules to determine the taboo cells;
     Rule 1: if a cell is a corner and not a target, then it is a taboo cell.
     Rule 2: all the cells between two corners along a wall are taboo if none of
             these cells is a target.

    @param warehouse:
        a Warehouse object with a worker inside the warehouse

    @return
       A string representing the puzzle with only the wall cells marked with
       a '#' and the taboo cells marked with a 'X'.
       The returned string should NOT have marks for the worker, the targets,
       and the boxes.
    '''

    # Unnecessary symbols to be removed
    remove = ['.', '!', '*', '@', '$']

    # Convert warehouse object to a string
    wh_str = str(warehouse)
    # Convert warehouse string to a 2D array
    wh = ([list(line) for line in wh_str.split('\n')])

    # Get coordinate of each taboo cell
    taboo_coord = taboo_coords(warehouse)

    # Replace taboo cells in warehouse array with 'X' symbol
    for i in taboo_coord:
        wh[i[1]][i[0]] = 'X'

    # Join array into string
    taboo_str = "\n".join("".join(cell) for cell in wh)

    # Remove other symbols
    for i in remove:
        taboo_str = taboo_str.replace(i, ' ')

    return taboo_str


def is_corner(wh_str, current_cell):
    '''
    Checks whether cell is a corner or not.

    @param warehouse:
        a Warehouse object with a worker inside the warehouse
    @param current_cell:
        [x, y] coords of current cell
    @return
       True if current cell has a wall above/below it AND a wall to the left/right
       of it. Otherwise return false if
        current cell is not a corner.
    '''

    wall_cell = '#'
    target = '.'
    x, y = current_cell[0], current_cell[1]
    above, below = y - 1, y + 1
    left, right = x - 1, x + 1
    # Cell is a corner if it is not a target, and if there is a wall
    # above/below cell and to the left/right of cell.
    if ((wh_str[y][x] != target) and
            (wh_str[above][x] == wall_cell or wh_str[below][x] == wall_cell) and
            (wh_str[y][left] == wall_cell or wh_str[y][right] == wall_cell)):
        return True
    else:
        return False


def is_btwn_corner(wh_str, warehouse, corners):
    '''
    Checks whether cell is in between a corner or not
    @param wh_str:
        a Warehouse string
    @param warehouse:
        a Warehouse object with a worker inside the warehouse
    @param corners:
        array of all the corner cells in the warehouse
    @return
       List of all taboo cells
    '''
    corner_pairs = list(combinations(corners, 2))
    extra_taboo_list = []
    for corner in corner_pairs:
        # Check to see if pair of corners are on the same column
        walls_beside = 0

        if (corner[0][0] == corner[1][0]):
            if corner[0][1] < corner[1][1]:
                min_y = corner[0][1]
                max_y = corner[1][1]
            else:
                min_y = corner[1][1]
                max_y = corner[0][1]
            # Loop through each cell in between corner
            for cell_between in range(min_y + 1, max_y):
                left, right = corner[0][0] - 1, corner[0][0] + 1
                # If the cell is a wall or a target it is not a taboo cell
                if ((corner[0][0], cell_between) in warehouse.walls or
                        (corner[0][0], cell_between) in warehouse.targets):
                    break
                else:
                    # Check if there is a wall to the left or right of cell
                    if (((wh_str[cell_between][left]) == '#') or
                            ((wh_str[cell_between][right]) == '#')):
                        walls_beside += 1
                    # Check if looped through all cells in between corner and
                    # check if every cell in between is next to a wall
                    if (cell_between == max_y - 1 and walls_beside == max_y - min_y - 1):
                        for cell_between in range(min_y + 1, max_y):
                            # Add cells in between the two corners as taboo cells
                            extra_taboo_list.append((corner[0][0], cell_between))

        # Check to see if pair of corners are on the same row
        if (corner[0][1] == corner[1][1]):
            if corner[0][0] < corner[1][0]:
                min_x = corner[0][0]
                max_x = corner[1][0]
            else:
                min_x = corner[1][0]
                max_x = corner[0][0]
            # Loop through each cell in between corner
            for cell_between in range(min_x + 1, max_x):
                above, below = corner[0][1] - 1, corner[0][1] + 1
                if ((cell_between, corner[0][1]) in warehouse.walls or
                        (cell_between, corner[0][1]) in warehouse.targets):
                    break
                else:
                    if (((wh_str[above][cell_between]) == '#') or
                            ((wh_str[below][cell_between]) == '#')):
                        walls_beside += 1
                    if (cell_between == max_x - 1 and walls_beside == max_x - min_x - 1):
                        for cell_between in range(min_x + 1, max_x):
                            extra_taboo_list.append((cell_between, corner[0][1]))
    return extra_taboo_list


def valid_cells(warehouse):
    '''
    Checks whether non-wall cells are within the wall boundaries.

    @param warehouse:
        a Warehouse object with a worker inside the warehouse
    @return
       List of all valid cells within walls
    '''

    # Get coordinates of walls
    wall_cells = warehouse.walls
    every_wall_x = [x for x, y in wall_cells]
    every_wall_y = [y for x, y in wall_cells]

    # Get coordinates of every single cell on map
    every_cell = [(x, y) for x in range(max(every_wall_x) + 1) \
                  for y in range(max(every_wall_y) + 1)]

    # Get coordinates of every single cell on map which is not a wall
    every_valid_floor_cell = [(x, y) for (x, y) in every_cell if (x, y) \
                              not in wall_cells]

    # List of all y-coordinates of each wall in each column
    vert_walls = [[] for x in range(max(every_wall_x) + 1)]
    for x, y in wall_cells:
        vert_walls[x].append(y)

    # Delete each cell which goes over the last wall boundary
    for i in reversed(every_valid_floor_cell):
        if (i[1] > max(vert_walls[i[0]]) or
                i[1] < min(vert_walls[i[0]])):
            every_valid_floor_cell.remove(i)

    return every_valid_floor_cell


def taboo_coords(warehouse):
    '''
    Returns a list of coords of all taboo cells

    @param warehouse:
        a Warehouse object with a worker inside the warehouse
    @return
       List of coords of all taboo cells
    '''

    warehouse_str = str(warehouse)
    warehouse_str = ([list(line) for line in warehouse_str.split('\n')])

    # Get every valid cell inside the wall boundaries
    every_valid_cell = valid_cells(warehouse)
    taboo_list = []

    for cell in every_valid_cell:
        # Add corner cells as taboo (Rule 1)
        if (is_corner(warehouse_str, (cell[0], cell[1]))):
            taboo_list.append((cell[0], cell[1]))
    # Add cells between corners as taboo (Rule 2)
    other_taboo = is_btwn_corner(warehouse_str, warehouse, taboo_list)
    taboo_list = taboo_list + other_taboo
    return taboo_list


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class SokobanPuzzle(search.Problem):
    '''
    An instance of the class 'SokobanPuzzle' represents a Sokoban puzzle.
    An instance contains information about the walls, the targets, the boxes
    and the worker.

    Your implementation should be fully compatible with the search functions of
    the provided module 'search.py'.

    Each SokobanPuzzle instance should have at least the following attributes
    - self.allow_taboo_push
    - self.macro

    When self.allow_taboo_push is set to True, the 'actions' function should
    return all possible legal moves including those that move a box on a taboo
    cell. If self.allow_taboo_push is set to False, those moves should not be
    included in the returned list of actions.

    If self.macro is set True, the 'actions' function should return
    macro actions. If self.macro is set False, the 'actions' function should
    return elementary actions.
    '''

    def __init__(self, warehouse,push_costs = None, macro = True):
        self.taboo_cells = tuple(taboo_cells(warehouse))
        self.initial = (tuple(warehouse.worker),)+tuple(warehouse.boxes)
        self.allow_taboo_push = True
        self.goals = tuple(warehouse.targets)
        self.walls = tuple(warehouse.walls)
        self.targets = tuple(warehouse.targets)
        self.push_costs = push_costs
        self.macro = macro
        self.warehouse=warehouse

    def actions(self, state):
        """
        Return the list of actions that can be executed in the given state.

        As specified in the header comment of this class, the attributes
        'self.allow_taboo_push' and 'self.macro' should be tested to determine
        what type of list of actions is to be returned.
        """
        # Change to state if we get a warehouse object
        if type(state) == sokoban.Warehouse:
            state=(tuple(state.worker),)+tuple(state.boxes)
        # Get worker and box coordinates
        workerX, workerY = state[0]
        boxes = state[1:]
        allowedMoves = []
        # macro mode
        if self.macro:
            for box in boxes:
                boxX, boxY = box
                if (boxX-1, boxY) not in self.walls:
                    if (boxX-1, boxY) not in boxes:
                        if can_go_there(self.warehouse, (boxY, boxX+1)):
                            if self.allow_taboo_push:
                                allowedMoves.append((box, "Left"))
                            elif (boxX-1, boxY) not in self.taboo_cells:
                                allowedMoves.append((box, "Left"))
                if (boxX, boxY-1) not in self.walls:
                    if (boxX, boxY-1) not in boxes:
                        if can_go_there(self.warehouse, (boxY+1, boxX)):
                            if self.allow_taboo_push:
                                allowedMoves.append((box, "Up"))
                            elif (boxX, boxY-1) not in self.taboo_cells:
                                allowedMoves.append((box, "Up"))
                if (boxX+1, boxY) not in self.walls:
                    if (boxX+1, boxY) not in boxes:
                        if can_go_there(self.warehouse, (boxY, boxX-1)):
                            if self.allow_taboo_push:
                                allowedMoves.append((box, "Right"))
                            elif (boxX+1, boxY) not in self.taboo_cells:
                                allowedMoves.append((box, "Right"))
                if (boxX, boxY+1) not in self.walls:
                    if (boxX, boxY+1) not in boxes:
                        if can_go_there(self.warehouse, (boxY-1, boxX)):
                            if self.allow_taboo_push:
                                allowedMoves.append((box, "Down"))
                            elif (boxX, boxY+1) not in self.taboo_cells:
                                allowedMoves.append((box, "Down"))
        else:
            # Elem mode
            if (workerX - 1, workerY) not in self.walls:
                if (workerX - 1, workerY) not in boxes:
                    allowedMoves.append("Left")
                else:
                    if (workerX - 2, workerY) not in self.walls:
                        if (workerX - 2, workerY) not in boxes:
                            if (self.allow_taboo_push):
                                allowedMoves.append("Left")
                            elif (workerX - 2, workerY) not in self.taboo_cells:
                                allowedMoves.append("Left")
            if (workerX, workerY - 1) not in self.walls:
                if (workerX, workerY - 1) not in boxes:
                    allowedMoves.append("Up")
                else:
                    if (workerX, workerY - 2) not in self.walls:
                        if (workerX, workerY -2) not in boxes:
                            if (self.allow_taboo_push):
                                allowedMoves.append("Up")
                            elif (workerX, workerY - 2) not in self.taboo_cells:
                                allowedMoves.append("Up")
            if (workerX + 1, workerY) not in self.walls:
                if (workerX + 1, workerY) not in boxes:
                    allowedMoves.append("Right")
                else:
                    if (workerX + 2, workerY) not in self.walls:
                        if (workerX + 2, workerY) not in boxes:
                            if (self.allow_taboo_push):
                                allowedMoves.append("Right")
                            elif (workerX + 2, workerY) not in self.taboo_cells:
                                allowedMoves.append("Right")
            if (workerX, workerY + 1) not in self.walls:
                if (workerX, workerY + 1) not in boxes:
                    allowedMoves.append("Down")
                else:
                    if (workerX, workerY + 2) not in self.walls:
                        if (workerX, workerY + 2) not in boxes:
                            if (self.allow_taboo_push):
                                allowedMoves.append("Down")
                            elif (workerX, workerY + 2) not in self.taboo_cells:
                                allowedMoves.append("Down")
        return allowedMoves


    def result(self, state, action):

        assert action in self.actions(state)  # defensive programming!
        
        # Change to state if we get a warehouse object
        if type(state) == sokoban.Warehouse:
            state=(tuple(state.worker),)+tuple(state.boxes)
        # Get worker and box coordinates
        next_state = deepcopy(state)
        new_worker = list(next_state[0])
        new_boxes = list(next_state[1:])
        # Macro mode
        if self.macro:
            new_worker=action[0] # Get worker xy
            action=action[1] # Get moving direction
            boxNum = new_boxes.index(tuple(new_worker)) # Get index of the box
            box = list(new_boxes[boxNum]) # Get the box to be moved
            # Move the box
            if (action == "Left"):                         
                box[0] -= 1
                new_boxes[boxNum] = tuple(box)
            if (action == "Up"):                
                box[1] -= 1
                new_boxes[boxNum] = tuple(box)
            if (action == "Right"):  
                box[0] += 1
                new_boxes[boxNum] = tuple(box)
            if (action == "Down"):                
                box[1] += 1
                new_boxes[boxNum] = tuple(box)
            # Update the warehouse
            self.warehouse.boxes=tuple(new_boxes)
            self.warehouse.worker=tuple(new_worker)
        else:
            if action == 'Left':
                new_worker = (new_worker[0] - 1, new_worker[1])
                if new_worker in new_boxes:
                    newBox = (new_worker[0] - 1, new_worker[1])
                    if newBox not in self.walls and new_boxes:
                        new_boxes[new_boxes.index(new_worker)] = newBox
                    else:
                        return "Can't push"

            if action == 'Right':
                new_worker = (new_worker[0] + 1, new_worker[1])
                if new_worker in new_boxes:
                    newBox = (new_worker[0] + 1, new_worker[1])
                    if newBox not in self.walls and newBox not in new_boxes:
                        new_boxes[new_boxes.index(new_worker)] = newBox
                    else:
                        return "Can't push"

            if action == 'Up':
                new_worker = (new_worker[0], new_worker[1] - 1)
                if new_worker in new_boxes:
                    newBox = (new_worker[0], new_worker[1] - 1)
                    if newBox not in self.walls and new_boxes:
                        new_boxes[new_boxes.index(new_worker)] = newBox
                    else:
                        return "Can't push"

            if action == 'Down':
                new_worker = (new_worker[0], new_worker[1] + 1)
                if new_worker in new_boxes:
                    newBox = (new_worker[0], new_worker[1] + 1)
                    if newBox not in self.walls and new_boxes:
                        new_boxes[new_boxes.index(new_worker)] = newBox
                    else:
                        return "Can't push"

        next_state = (tuple(new_worker),)+tuple(new_boxes)

        return next_state

    

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal, as specified in the constructor. Override this
        method if checking against a single self.goal is not enough."""

        # If any box is not on a goal, this is not the goal state
        for i in state[1:]:
            if i not in self.goals:
                return False
        return True

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        if self.push_costs == None:
            return c + 1
        else:
            state1_boxes = state1[1:]
            state2_boxes = state2[1:]
            if state1_boxes != state2_boxes:
                for nth_box in range(len(state1_boxes)):
                    if (state1_boxes[nth_box] != state2_boxes[nth_box]):
                        index = nth_box
                        return c + self.push_costs[index]
            else:
                return c + 1

    def list_solution(self, goal_node):
        """
            Shows solution represented by a specific goal node.
            For example, goal node could be obtained by calling
                goal_node = breadth_first_tree_search(problem)
        """
        # path is list of nodes from initial state (root of the tree)
        # to the goal_node
        if goal_node == None:
            return "Impossible"
        #print("goalnode", goal_node)
        path = goal_node.path()
        # print the solution
        path_list = []

        for node in path:
            if node.action is not None:
                path_list.append(node.action)
        return path_list

    def h(self, node):
        """Heuristic for the sliding puzzle: returns distance between boxes and targets"""
        boxes = node.state[1:]
        targets = list(self.targets)
        heur = 0
        # Find the closest target for each box
        for box in boxes:
            closest_target = targets[0] # init closest target as first target
            for target in targets:
                if (manhattan_dist(target, box) < manhattan_dist(closest_target, box)):
                    closest_target = target
            heur = heur + manhattan_dist(closest_target, box)

        return heur

def manhattan_dist(obj1,obj2):
    return abs(obj1[1]-obj2[1]) + abs(obj1[0] - obj2[0])
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def check_elem_action_seq(warehouse, action_seq):
    '''

    Determine if the sequence of actions listed in 'action_seq' is legal or not.

    Important notes:
      - a legal sequence of actions does not necessarily solve the puzzle.
      - an action is legal even if it pushes a box onto a taboo cell.

    @param warehouse: a valid Warehouse object

    @param action_seq: a sequence of legal actions.
           For example, ['Left', 'Down', Down','Right', 'Up', 'Down']

    @return
        The string 'Impossible', if one of the action was not successul.
           For example, if the agent tries to push two boxes at the same time,
                        or push one box into a wall.
        Otherwise, if all actions were successful, return
               A string representing the state of the puzzle after applying
               the sequence of actions.  This must be the same string as the
               string returned by the method  Warehouse.__str__()
    '''

    puzzle = SokobanPuzzle(warehouse, macro = False)
    myWarehouse = warehouse
    for action in action_seq:
        if (action in puzzle.actions(myWarehouse)):
            state = puzzle.result(myWarehouse, action)
            myWarehouse.worker=state[0]
            myWarehouse.boxes=state[1:]
        else:
            return "Impossible"
    return myWarehouse.__str__()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def solve_sokoban_elem(warehouse):
    '''
    This function should solve using A* algorithm and elementary actions
    the puzzle defined in the parameter 'warehouse'.

    In this scenario, the cost of all (elementary) actions is one unit.

    @param warehouse: a valid Warehouse object

    @return
        If puzzle cannot be solved return the string 'Impossible'
        If a solution was found, return a list of elementary actions that solves
            the given puzzle coded with 'Left', 'Right', 'Up', 'Down'
            For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
            If the puzzle is already in a goal state, simply return []
    '''

    sp = SokobanPuzzle(warehouse, macro = False)

    sol = search.astar_graph_search(sp)

    list_elem_actions = sp.list_solution(sol)

    return list_elem_actions



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class can_go_puzzle(search.Problem):
    def __init__(self, warehouse, goal):
        self.taboo_cells = tuple(taboo_cells(warehouse))
        self.initial = (tuple(warehouse.worker),) + tuple(warehouse.boxes)
        self.allow_taboo_push = True
        self.goals = tuple(goal)
        self.walls = tuple(warehouse.walls)
        self.boxes = tuple(warehouse.boxes)
        self.targets = tuple(warehouse.targets)

    def actions(self, state):
        """
        Return the list of actions that can be executed in the given state.

        As specified in the header comment of this class, the attributes
        'self.allow_taboo_push' and 'self.macro' should be tested to determine
        what type of list of actions is to be returned.
        """
        workerX, workerY = state[0]
        boxes = state[1:]
        allowedMoves = []
        if (workerX - 1, workerY) not in self.walls:
            if (workerX - 1, workerY) not in boxes:
                allowedMoves.append("Left")
        if (workerX, workerY - 1) not in self.walls:
            if (workerX, workerY - 1) not in boxes:
                allowedMoves.append("Up")
        if (workerX + 1, workerY) not in self.walls:
            if (workerX + 1, workerY) not in boxes:
                allowedMoves.append("Right")

        if (workerX, workerY + 1) not in self.walls:
            if (workerX, workerY + 1) not in boxes:
                allowedMoves.append("Down")
        return allowedMoves


    def result(self, state, action):

        assert action in self.actions(state)  # defensive programming!

        next_state = deepcopy(state)
        new_worker = list(next_state[0])

        if action == 'Left':
            new_worker = (new_worker[0] - 1, new_worker[1])

        if action == 'Right':
            new_worker = (new_worker[0] + 1, new_worker[1])

        if action == 'Up':
            new_worker = (new_worker[0], new_worker[1] - 1)

        if action == 'Down':
            new_worker = (new_worker[0], new_worker[1] + 1)

        next_state = (tuple(new_worker),) + next_state[1:]
        return next_state

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal, as specified in the constructor. Override this
        method if checking against a single self.goal is not enough."""
        # Check if worker is at goal position
        return state[0] == self.goals

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def list_solution(self, goal_node):
        """
            Shows solution represented by a specific goal node.
            For example, goal node could be obtained by calling
                goal_node = breadth_first_tree_search(problem)
        """
        # path is list of nodes from initial state (root of the tree)
        # to the goal_node
        if goal_node == None:
            return "Impossible"
        path = goal_node.path()
        path_list = []
        for node in path:
            if node.action is not None:
                path_list.append(node.action)
        return path_list


def can_go_there(warehouse, dst):
    '''
    Determine whether the worker can walk to the cell dst=(row,column)
    without pushing any box.

    @param warehouse: a valid Warehouse object

    @return
      True if the worker can walk to cell dst=(row,column) without pushing any box
      False otherwise
    '''
    #swap x and y to work with pre-existing code
    row = dst[0]
    col = dst[1]

    goal = [col, row]

    if (warehouse.worker == goal):
        return True

    cgt_sp = can_go_puzzle(warehouse, goal)
    cgt_sol = search.breadth_first_graph_search(cgt_sp)
    list_actions = cgt_sp.list_solution(cgt_sol) 
    
    #return true if the if it is possible for the worker to go to dst
    if (list_actions == "Impossible"):
        return False
    else:
        return True


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def solve_sokoban_macro(warehouse):
    '''
    Solve using using A* algorithm and macro actions the puzzle defined in
    the parameter 'warehouse'.

    A sequence of macro actions should be
    represented by a list M of the form
            [ ((r1,c1), a1), ((r2,c2), a2), ..., ((rn,cn), an) ]
    For example M = [ ((3,4),'Left') , ((5,2),'Up'), ((12,4),'Down') ]
    means that the worker first goes the box at row 3 and column 4 and pushes it left,
    then goes to the box at row 5 and column 2 and pushes it up, and finally
    goes the box at row 12 and column 4 and pushes it down.

    In this scenario, the cost of all (macro) actions is one unit.

    @param warehouse: a valid Warehouse object

    @return
        If the puzzle cannot be solved return the string 'Impossible'
        Otherwise return M a sequence of macro actions that solves the puzzle.
        If the puzzle is already in a goal state, simply return []
    '''

    wh = warehouse
    sp = SokobanPuzzle(wh, macro = True)
    sol = search.astar_graph_search(sp)
    M=[]

    if sol is None:
        return ['Impossible']
    else:
        for action in sol.solution():
            if action is not None:
                M.append(((action[0][1], action[0][0]), action[1]))
        return M

def solve_weighted_sokoban_elem(warehouse, push_costs):
    '''
    In this scenario, we assign a pushing cost to each box, whereas for the
    functions 'solve_sokoban_elem' and 'solve_sokoban_macro', we were
    simply counting the number of actions (either elementary or macro) executed.

    When the worker is moving without pushing a box, we incur a
    cost of one unit per step. Pushing the ith box to an adjacent cell
    now costs 'push_costs[i]'.

    The ith box is initially at position 'warehouse.boxes[i]'.

    This function should solve using A* algorithm and elementary actions
    the puzzle 'warehouse' while minimizing the total cost described above.

    @param
     warehouse: a valid Warehouse object
     push_costs: list of the weights of the boxes (pushing cost)

    @return
        If puzzle cannot be solved return 'Impossible'
        If a solution exists, return a list of elementary actions that solves
            the given puzzle coded with 'Left', 'Right', 'Up', 'Down'
            For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
            If the puzzle is already in a goal state, simply return []
    '''

    wh = SokobanPuzzle(warehouse,push_costs, macro = False)
    sol = search.astar_graph_search(wh)


    list_elem_actions = wh.list_solution(sol)

    return list_elem_actions

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

