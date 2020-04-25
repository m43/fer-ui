import parameters
from algorithms.astar import a_star
from algorithms.bfs import breadthFirstSearch
from algorithms.hcheck import *
from algorithms.ucs import uniform_cost_search
from data_loader import *

if __name__ == '__main__':
    ss = PuzzleStateSpace("876_543_21x", "123_456_78x")

    print("Loaded puzzle state space with \"{}\" as start space and \"{}\" as goal.".format(ss.get_start_state(),
                                                                                            ss.get_goal_state()))

    print('----> BFS')
    breadthFirstSearch(ss.get_start_state(), ss.successor, ss.is_goal_state)

    print('----> UCS')
    uniform_cost_search(ss.get_start_state(), ss.successor, ss.is_goal_state)

    print("####################")
    print("### Heuristic L0 ###")
    print("####################")
    print("")
    print('----> A*')
    a_star(ss.get_start_state(), ss.successor, ss.is_goal_state, ss.heuristic_l0)
    print("----> Was the used heuristic optimistic?")
    _, err_a = check_heuristic_admissibility([ss.get_goal_state()], ss.predecessor, ss.heuristic_l0)
    print("----> Was the used heuristic consistent?")
    _, err_b = check_heuristic_consistency(ss.get_start_state(), [ss.get_goal_state()], ss.successor, ss.heuristic_l0)
    assert not err_a
    assert not err_b

    print("####################")
    print("### Heuristic L1 ###")
    print("####################")
    print("")
    print('----> A*')
    a_star(ss.get_start_state(), ss.successor, ss.is_goal_state, ss.heuristic_l1)
    print("----> Was the used heuristic optimistic?")
    _, err_a = check_heuristic_admissibility([ss.get_goal_state()], ss.predecessor, ss.heuristic_l1)
    print("----> Was the used heuristic consistent?")
    _, err_b = check_heuristic_consistency(ss.get_start_state(), [ss.get_goal_state()], ss.successor, ss.heuristic_l1)
    assert not err_a
    assert not err_b
