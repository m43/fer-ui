import parameters
from algorithms.astar import *
from algorithms.bfs import *
from algorithms.hcheck import check_heuristic_admissibility, check_heuristic_consistency
from algorithms.ucs import *
from data_loader import DataLoader


# TODO note that all the functionality written is under the hypothesis that there will be no double edges between
#  same node (for example, one cannot cat from Pula to Vodnjan in using two paths, but only the best path will be
#  given to start with) in the input file

def run(path_to_state_space_definition, path_to_heuristic_definition):
    # Load state space and the heuristic function
    number_of_states, start_state, goal_states, successor, predecessor, goal, number_of_transitions = DataLoader.laod_state_space(
        path_to_state_space_definition)
    h = DataLoader.load_heuristic(path_to_heuristic_definition)

    print("Loaded {} states with {} transitions".format(number_of_states, number_of_transitions))
    print("Start state is: {}".format(start_state))
    print("Goal states are: {}".format(goal_states))
    print()

    print('----> BFS')
    breadthFirstSearch(start_state, successor, goal)

    print('----> UCS')
    uniform_cost_search(start_state, successor, goal)

    print('----> A*')
    a_star(start_state, successor, goal, h)

    print("----> Was the used heuristic optimistic?")
    check_heuristic_admissibility(goal_states, predecessor, h)

    print("----> Was the used heuristic consistent?")
    check_heuristic_consistency(goal_states, successor, predecessor, h)

    print("\n\n\n\n\n")


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
