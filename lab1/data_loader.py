class DataLoader:
    @staticmethod
    def laod_state_space(path_to_state_space_definition):
        start_state = None
        goal_states = None
        transitions_from_state = {}  # For example { "Pula": [(Vodnjan,12), (Barban,28), (Medulin,9)], ...}
        transitions_into_state = {}
        with open(path_to_state_space_definition, "r+") as file:
            for line in file.readlines():
                line = line.strip()
                if line.startswith("#"):
                    continue

                if not start_state:
                    start_state = line.strip()
                elif not goal_states:
                    goal_states = set(line.strip().split())
                else:
                    line_parts = line.split(":")
                    assert len(line_parts) == 2

                    if not line_parts[1]:
                        transitions_from_state[line_parts[0]] = []
                    else:
                        successors = list(map(lambda x: (x[0], float(x[1])),
                                              map(lambda x: x.split(","), line_parts[1].strip().split(" "))))
                        transitions_from_state[line_parts[0]] = successors
                        for successor in successors:
                            if successor[0] not in transitions_into_state:
                                transitions_into_state[successor[0]] = []

                            transitions_into_state[successor[0]].append((line_parts[0], successor[1]))

        assert start_state
        assert goal_states

        number_of_states = len(transitions_from_state)
        number_of_transitions = sum(map(lambda item: len(item[1]), transitions_from_state.items()))
        successor = lambda state: transitions_from_state[state] if state in transitions_from_state else []
        predecessor = lambda state: transitions_into_state[state] if state in transitions_into_state else []
        goal = lambda state: state in goal_states

        return number_of_states, start_state, goal_states, successor, predecessor, goal, number_of_transitions

    @staticmethod
    def load_heuristic(path_to_heuristic_definition):
        heuristic = {}
        with open(path_to_heuristic_definition, "r+") as file:
            for line in file.readlines():
                line = line.strip()
                if line.startswith("#"):
                    continue

                city, value = line.split(":")
                heuristic[city] = float(value.strip())

        return lambda state: heuristic[state] if state in heuristic else 0
