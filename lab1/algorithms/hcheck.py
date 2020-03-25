import time
from heapq import *

from sortedcontainers import SortedList


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
        if total_cost < h(state):
            contradiction_count += 1
            if contradiction_count <= 50:
                output += "[ERR] h({}) > h*({}): {} > {}\n".format(state, state, h(state), total_cost)

    print("Delta t:", time.time() - timestamp, "seconds")

    if contradiction_count > 0:
        if contradiction_count > 50:
            print("As there are many errors, printing will be omitted. Consider the error/contradiction count.")
        else:
            print(output)
        print("Heuristic is not optimistic. Found {} contradictions in state space".format(
            contradiction_count))
    else:
        print("Heuristic is optimistic for all states that could be visited from the goal state.")

    print()


def check_heuristic_consistency(goal_states, successor, predecessor, h):
    timestamp = time.time()

    # dijkstra to make a tree from the goal state, following the monotonic growth of h*
    closed_front_dict = {}  # state --> total cost aka h*

    open_front = SortedList(key=lambda x: -x[1])  # stores tuples: (state, total cost of getting to this node aka h*)
    open_front.update([(s, 0) for s in goal_states])

    contradiction_count = 0
    output = ""
    while len(open_front) != 0:
        x = open_front.pop()
        if x[0] in closed_front_dict:
            continue

        closed_front_dict[x[0]] = x[1]
        for (s, c) in predecessor(x[0]):
            if s not in closed_front_dict or closed_front_dict[s] > x[1] + c:
                open_front.add((s, x[1] + c))
        for (s, c) in successor(x[0]):
            if not h(s) >= h(x[0]) - c:
                contradiction_count += 1
                if contradiction_count <= 50:
                    output += "[ERR] h({}) < h({}) - c: {} < {} - {}\r\n".format(s, x[0], h(s), h(x[0]), c)

    print("Delta t:", time.time() - timestamp, "seconds")

    if contradiction_count == 0:
        if contradiction_count > 50:
            print("As there are many errors, printing will be omitted. Consider the contradiction aka error count.")
        else:
            print(output)
        print("Heuristic is consistent")
    else:
        print("Heuristic is not consistent. Found {} contradictions".format(contradiction_count))

    print()
