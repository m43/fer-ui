class StateSpace:

    def __init__(self, path_to_state_space_definition):
        self._start_state = None
        self._goal_states = None
        self._states = set()

        self._transitions_from_state = {}  # For example { "Pula": [(Vodnjan,12), (Barban,28), (Medulin,9)], ...}
        self._transitions_into_state = {}
        self._number_of_transitions = 0

        self._load_from_file(path_to_state_space_definition)

    def _load_from_file(self, path):
        with open(path, "r+") as file:
            for line in file.readlines():
                line = line.strip()
                if line.startswith("#") or len(line) == 0:
                    continue

                if not self._start_state:
                    self._start_state = line.strip()
                    self._states.add(self._start_state)
                elif not self._goal_states:
                    self._goal_states = set(line.strip().split())
                    self._states.update(self._goal_states)
                else:
                    line_parts = line.split(":")
                    assert len(line_parts) == 2

                    current_state = line_parts[0]
                    self._states.add(current_state)
                    if current_state not in self._transitions_from_state:
                        self._transitions_from_state[current_state] = []

                    if line_parts[1]:
                        for successor_parts in map(lambda x: x.split(","), line_parts[1].strip().split(" ")):
                            successor = (successor_parts[0], float(successor_parts[1]))
                            self._transitions_from_state[current_state].append((successor[0], successor[1]))

                            if successor[0] not in self._transitions_into_state:
                                self._transitions_into_state[successor[0]] = []
                            self._transitions_into_state[successor[0]].append((line_parts[0], successor[1]))

        assert self._start_state
        assert self._goal_states

        self._number_of_transitions = sum(map(lambda item: len(item[1]), self._transitions_from_state.items()))

    def get_number_of_transitions(self):
        return self._number_of_transitions

    def get_states(self):
        return self._states

    def get_start_state(self):
        return self._start_state

    def get_goal_states(self):
        return self._goal_states

    def get_number_of_states(self):
        return len(self._states)

    def predecessor(self, state):
        return self._transitions_into_state[state] if state in self._transitions_into_state else []

    def successor(self, state):
        return self._transitions_from_state[state] if state in self._transitions_from_state else []

    def is_goal_state(self, state):
        return state in self._goal_states


class HeuristicLoader:
    def __init__(self, path_to_heuristic_definition):
        self._heuristic = {}
        self._load_from_path(path_to_heuristic_definition)

    def _load_from_path(self, path):
        with open(path, "r+") as file:
            for line in file.readlines():
                line = line.strip()
                if line.startswith("#"):
                    continue

                state, prediction = line.split(":")
                self._heuristic[state] = float(prediction.strip())

    def predict(self, state):
        return self._heuristic[state] if state in self._heuristic else 0
