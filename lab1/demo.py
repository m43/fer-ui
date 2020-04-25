import parameters
from algorithms.astar import *
from algorithms.bfs import *
from algorithms.hcheck import *
from algorithms.ucs import *
from data_loader import *


# TODO note that all the functionality written is under the hypothesis that there will be no double edges between
#  same node (for example, one cannot cat from Pula to Vodnjan in using two paths, but only the best path will be
#  given to start with) in the input file

def run(path_to_state_space_definition, path_to_heuristic_definition):
    # Load state space and the heuristic
    ss = StateSpace(path_to_state_space_definition)
    h = HeuristicLoader(path_to_heuristic_definition)

    print("Loaded {} states with {} transitions".format(ss.get_number_of_states(), ss.get_number_of_transitions()))
    print("Start state is: {}".format(ss.get_start_state()))
    print("Goal states are: {}".format(ss.get_goal_states()))
    print()

    print('----> BFS')
    breadthFirstSearch(ss.get_start_state(), ss.successor, ss.is_goal_state)

    print('----> UCS')
    uniform_cost_search(ss.get_start_state(), ss.successor, ss.is_goal_state)

    print('----> A*')
    a_star(ss.get_start_state(), ss.successor, ss.is_goal_state, h.predict)

    print("----> Was the used heuristic optimistic?")
    check_heuristic_admissibility(ss.get_goal_states(), ss.predecessor, h.predict)

    print("----> Was the used heuristic consistent?")
    check_heuristic_consistency(ss.get_start_state(), ss.get_goal_states(), ss.successor, h.predict)
    print("----> Was the used heuristic consistent? (Faster check with all states given)")
    check_heuristic_consistency_with_known_states(ss.get_states(), ss.successor, h.predict)

    # print("\n\n\n")


if __name__ == '__main__':
    print("This demonstration file runs three algorithms for finding a solution in state space of the defined "
          "problem. The first algorithm is Breadth First Search, the second algorithm is Uniform Cost Search and the "
          "third is A*. Afterwards, the heuristic function is checked for admissibility and consistency.")

    run(parameters.AI_STATE_SPACE, parameters.AI_PASS_HEURISTIC)
    run(parameters.AI_STATE_SPACE, parameters.AI_FAIL_HEURISTIC)

    run(parameters.ISTRIA_STATE_SPACE, parameters.ISTRIA_CONSISTENT_HEURISTIC)
    run(parameters.ISTRIA_STATE_SPACE, parameters.ISTRIA_PESSIMISTIC_HEURISTIC)

    run(parameters.PUZZLE_3X3_STATE_SPACE, parameters.PUZZLE_3X3_MISPLACED_HEURISTIC)
    run(parameters.PUZZLE_3X3_STATE_SPACE_UNSOLVABLE, parameters.PUZZLE_3X3_MISPLACED_HEURISTIC)
