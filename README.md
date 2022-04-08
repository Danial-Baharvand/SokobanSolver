# SokobanSolver
Sokoban is a computer puzzle game in which the player pushes boxes around a maze in order to
place them in designated locations. It was originally published in 1982 for the Commodore 64 and
IBM-PC and has since been implemented in numerous computer platforms and video game
consoles. SocobanSolver uses A* search algorithm to solve the Socoban puzzle for a player agent given a warehouse object.

While Sokoban is just a game,
it models a robot moving boxes in a warehouse and as such, it can be treated as an automated
planning problem. Sokoban is an interesting challenge for the field of artificial intelligence largely
due to its difficulty. Sokoban has been proven NP-hard. Sokoban is difficult not because of its
branching factor, but because of the huge depth of the solutions. Many actions (box pushes) are
needed to reach the goal state! However, given that the only available actions are moving the
worker up, down, left or right, the branching factor is small (only 4!). 

![image](https://user-images.githubusercontent.com/49452399/162423208-538b8499-9fa6-4622-a8ba-cd7fd916e2d0.png)

Illustration 1: Initial state of a warehouse. The green disk represents the
agent/robot/player, the brown squares represent the boxes/crates. The
black cells denote the target positions for the boxes. 

![image](https://user-images.githubusercontent.com/49452399/162423514-91c931a9-044b-470f-8f9a-aa58884b85fa.png)

Illustration 2: Goal state reached: all the boxes have been pushed to a
target position.

## Approach
As already mentioned, Sokoban has a large search space with few goals, located deep in the search
tree. However, admissible heuristics can be easily obtained. These properties suggest to approach
the problem with an informed search. Suitable generic algorithms include A* and its variations.
After playing for a few games, it is noticable that a bad move may leave the player in a doomed
state from which it is impossible to recover. For example, a box pushed into a corner cannot be
moved out. If that corner is not a goal, then the problem becomes unsolvable. We will call these
cells that should be avoided **taboo cells**. During a search, we can ignore the actions that move a box
on a taboo cell.

Another useful tool to reduce the search tree is to use **macro moves**. In the context of Sokoban, an
elementary action is a one-step move of the worker. A macro action is the decision of a manager to
have one specific box pushed to an adjacent cell. The macro action triggers itself an auxiliary
problem; can the worker go to the cell next to the specified box. Note that the macro action can be
translated into a sequence of elementary moves for the worker.

### Implemention

Approach 1 - Elementary Actions

In the first approach, all actions have the same cost. The actions are elementary in the sense
that an action moves the worker to an adjacent cell.

Approach 2 – Macro Actions

In the second approach, all actions still have the same cost. The actions are macro in the
sense that they focus on the motion of the boxes (not the many steps the worker has to do to
reach a box).

Approach 3 – Weighted Boxes

In this third approach, we assign a pushing cost to each box, whereas for the functions
solve_sokoban_elem and solve_sokoban_macro, we were simply counting the number of
actions executed (either elementary or macro). The actions in the third scenario are
elementary in the sense that an action moves the worker to an adjacent cell. 
