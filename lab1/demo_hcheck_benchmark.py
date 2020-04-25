import parameters
from algorithms.hcheck import *
from data_loader import *

if __name__ == '__main__':
    print("This demonstration file blah blah")

    # Load state space and the heuristic
    ss = StateSpace(parameters.PUZZLE_3X3_STATE_SPACE)
    h = HeuristicLoader(parameters.PUZZLE_3X3_MISPLACED_HEURISTIC)

    print("Loaded {} states with {} transitions".format(ss.get_number_of_states(), ss.get_number_of_transitions()))
    print()

    scores = []
    for (i, pair) in enumerate(parameters.PUZZLE_3X3__INIT_CONFIG_1):
        start_state = pair[0]

        print("#---> Configuration {}. <---#".format(i + 1))
        print("\tStart state is: {}".format(start_state))
        print("\tGoal states are (always the same): {}".format(ss.get_goal_states()))

        for j in range(10):
            print("----> Was the used heuristic optimistic?")
            delta_t_a, _ = check_heuristic_admissibility(ss.get_goal_states(), ss.predecessor, h.predict)
            print("----> Was the used heuristic consistent?")
            delta_t_b, _ = check_heuristic_consistency(start_state, ss.get_goal_states(), ss.successor, h.predict)
            print("----> Was the used heuristic consistent? (Faster check with all states given)")
            delta_t_c, _ = check_heuristic_consistency_with_known_states(ss.get_states(), ss.successor, h.predict)

            scores.append((delta_t_a, delta_t_b, delta_t_c))

    print("Final timing:")
    print(scores)
