import parameters
from algorithms.astar import a_star
from data_loader import *

if __name__ == '__main__':

    for start, end in parameters.PUZZLE_3X3__INIT_CONFIG_2:
        ss = PuzzleStateSpace(start, end)
        print("Loaded puzzle state space with \"{}\" as start space and \"{}\" as goal.".format(ss.get_start_state(),
                                                                                                ss.get_goal_state()))

        for h_name, h in [("Heuristic L0", ss.heuristic_l0),
                          ("Heuristic L1", ss.heuristic_l1)]:
            print("###", h_name)
            a_star(ss.get_start_state(), ss.successor, ss.is_goal_state, h)
