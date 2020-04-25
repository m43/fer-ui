import time
from heapq import *


def check_heuristic_admissibility(goal_states, predecessor, h):
    timestamp = time.time()

    closed_front_dict = {}  # state --> total cost aka h*
    open_front = []
    for s in goal_states:
        heappush(open_front, (0, (s, 0)))

    while open_front:
        x = heappop(open_front)[1]
        if x[0] in closed_front_dict:
            continue

        closed_front_dict[x[0]] = x[1]
        for (s, c) in predecessor(x[0]):
            if s not in closed_front_dict or closed_front_dict[s] > x[1] + c:
                heappush(open_front, ((x[1] + c), (s, x[1] + c)))

    # as h* is determined and saved in closed_front_dict, the check can be made
    contradiction_count = 0
    output = ""
    for (state, total_cost) in closed_front_dict.items():
        h_state = h(state)
        if total_cost < h_state:
            contradiction_count += 1
            if contradiction_count <= 50:
                output += "[ERR] h({}) > h*({}): {} > {}\n".format(state, state, h_state, total_cost)

    delta_t = time.time() - timestamp
    print("Delta t:", delta_t, "seconds")

    if contradiction_count > 0:
        if contradiction_count > 50:
            print("As there are many errors, printing will be omitted. Consider the error/contradiction count.")
        else:
            print(output)
        print("Heuristic is not optimistic. Found {} contradictions in state space".format(
            contradiction_count))
    else:
        print("Heuristic is optimistic for all states that could be visited from the goal state.")

    return delta_t, contradiction_count


def check_heuristic_consistency(start_state, goal_states, successor, h):
    timestamp = time.time()

    closed_front = set()

    open_front = set()
    open_front.add(start_state)
    open_front.update([s for s in goal_states])

    contradiction_count = 0
    output = ""
    while open_front:
        x = open_front.pop()
        closed_front.add(x)
        for (y, c) in successor(x):
            if y not in closed_front:
                open_front.add(y)

            h_from = h(x)
            h_to = h(y)
            if not h_to >= h_from - c:
                contradiction_count += 1
                if contradiction_count <= 50:
                    output += "[ERR] h({}) < h({}) - c: {} < {} - {}\r\n".format(h_to, h_from, h_to, h_from, c)

    delta_t = time.time() - timestamp
    print("Delta t:", delta_t, "seconds")

    if contradiction_count > 0:
        if contradiction_count > 50:
            print("As there are many errors, printing will be omitted. Consider the contradiction aka error count.")
        else:
            print(output)
        print("Heuristic is not consistent. Found {} contradictions".format(contradiction_count))
    else:
        print("Heuristic is consistent")

    return delta_t, contradiction_count


def check_heuristic_consistency_with_known_states(states, successor, h):
    timestamp = time.time()

    contradiction_count = 0
    output = ""
    for state in states:
        for (successor_state, cost) in successor(state):
            h_from = h(state)
            h_to = h(successor_state)
            if not h_to >= h_from - cost:
                contradiction_count += 1
                if contradiction_count <= 50:
                    output += "[ERR] h({}) < h({}) - c: {} < {} - {}\r\n".format(h_to, h_from, h_to, h_from, cost)

    delta_t = time.time() - timestamp
    print('Delta t:', delta_t, "seconds")

    if contradiction_count > 0:
        if contradiction_count > 50:
            print("As there are many errors, printing will be omitted. Consider the contradiction aka error count.")
        else:
            print(output)
        print("Heuristic is not consistent. Found {} contradictions".format(contradiction_count))
    else:
        print("Heuristic is consistent")

    return delta_t, contradiction_count
