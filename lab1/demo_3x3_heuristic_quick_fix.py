import parameters
from algorithms.astar import a_star
from algorithms.hcheck import *
from data_loader import *

if __name__ == '__main__':
    # Load state space and the heuristic
    ss = StateSpace(parameters.PUZZLE_3X3_STATE_SPACE)
    h = HeuristicLoader(parameters.PUZZLE_3X3_MISPLACED_HEURISTIC)

    h_predict_modified = lambda state: h.predict(state) / 2

    print("Loaded {} states with {} transitions".format(ss.get_number_of_states(), ss.get_number_of_transitions()))
    print("\tStart state is: {}".format(ss.get_start_state()))
    print("\tGoal states are (always the same): {}".format(ss.get_goal_states()))
    print()

    print('----> A*')
    a_star(ss.get_start_state(), ss.successor, ss.is_goal_state, h_predict_modified)

    print("----> Was the used heuristic optimistic?")
    _, err_a = check_heuristic_admissibility(ss.get_goal_states(), ss.predecessor, h_predict_modified)
    print("----> Was the used heuristic consistent?")
    _, err_b = check_heuristic_consistency(ss.get_start_state(), ss.get_goal_states(), ss.successor, h_predict_modified)
    print("----> Was the used heuristic consistent? (Faster check with all states given)")
    _, err_c = check_heuristic_consistency_with_known_states(ss.get_states(), ss.successor, h_predict_modified)

    assert not err_a
    assert not err_b
    assert not err_c
