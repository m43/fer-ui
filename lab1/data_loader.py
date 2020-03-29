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
        return self._transitions_into_state.get(state, [])

    def successor(self, state):
        return self._transitions_from_state.get(state, [])

    def is_goal_state(self, state):
        return state in self._goal_states


class PuzzleStateSpace:
    def __init__(self, start_state, goal_state):
        assert len(start_state) == 11
        assert len(goal_state) == 11

        self._start_state = start_state
        self._goal_state = goal_state

        self._goal_state_position_of_tiles, _ = PuzzleStateSpace._parse_state(goal_state)

    def get_start_state(self):
        return self._start_state

    def get_goal_state(self):
        return self._goal_state

    def is_goal_state(self, state):
        return state == self._goal_state

    @staticmethod
    def _parse_state(state):
        """

        Help function to parse a string state that represents puzzle states into the returned tuple of two arrays.

        First array represents the position of tiles in the state. It's an array of 9 numbers, each representing the
        positions of tiles. Index i in the array corresponds with the position of tile i, while index 0 corresponds with
        the position of the empty element.

        For example, that array would for the state 321_456_#78 look like this: [7, 3,2,1, 4,5,6, 8,9].

        The second array repesents tiles at position. For example 321_456_#78 would turn into [3,2,1, 4,5,6, #,7,8].

        The arrays are parsed all at once in this method in order to increase performance.
        # TODO  although, I think that splitting this would not decrease the performance very much, as it would increase
                readability...

        :param state: the state, like 321_456_#78
        :return: a tuple of two arrays, first telling the position of tiles and the second array is the other way around
        """

        position_of_tiles = [-1] * 9
        tiles_at_position = []
        position_counter = 1
        for c in state:
            if c == '_':
                continue
            elif c == 'x':
                position_of_tiles[0] = position_counter
                tiles_at_position.append("x")
            else:
                tile = int(c)
                position_of_tiles[tile] = position_counter
                tiles_at_position.append(tile)
            position_counter += 1

        return position_of_tiles, tiles_at_position

    @staticmethod
    def _construct_solution_with_swap(positions_array, swap_i, swap_j):
        temp = positions_array[swap_i - 1]
        positions_array[swap_i - 1] = positions_array[swap_j - 1]
        positions_array[swap_j - 1] = temp

        result = "{}{}{}_{}{}{}_{}{}{}".format(*positions_array)

        temp = positions_array[swap_i - 1]
        positions_array[swap_i - 1] = positions_array[swap_j - 1]
        positions_array[swap_j - 1] = temp

        return result, 1

    def predecessor(self, state):
        return self.successor(state)

    def successor(self, state):
        result = []

        tiles, slots = self._parse_state(state)

        empty_element_position = tiles[0]

        if (empty_element_position - 1) % 3 != 0:
            result.append(self._construct_solution_with_swap(slots, empty_element_position, empty_element_position - 1))
        if (empty_element_position - 1) % 3 != 2:
            result.append(self._construct_solution_with_swap(slots, empty_element_position, empty_element_position + 1))
        if 9 >= (empty_element_position - 3) >= 1:
            result.append(self._construct_solution_with_swap(slots, empty_element_position, empty_element_position - 3))
        if 9 >= (empty_element_position + 3) >= 1:
            result.append(self._construct_solution_with_swap(slots, empty_element_position, empty_element_position + 3))

        return result

    @staticmethod
    def pretty_print_state_string(state):
        return "\t{} {} {}\n\t{} {} {}\n\t{} {} {}\n".format(*(PuzzleStateSpace._parse_state(state)[1]))

    @staticmethod
    def pretty_print_state(state):
        print(PuzzleStateSpace.pretty_print_state_string(state))

    def heuristic_l0(self, state):
        tiles, _ = PuzzleStateSpace._parse_state(state)

        l1_sum = 0
        for tile_i in range(1, 9):
            l1_sum += not tiles[tile_i] == self._goal_state_position_of_tiles[tile_i]

        return l1_sum

    def heuristic_l1(self, state):
        tiles, _ = PuzzleStateSpace._parse_state(state)

        l1_sum = 0
        for tile_i in range(1, 9):
            given = tiles[tile_i] - 1
            goal = self._goal_state_position_of_tiles[tile_i] - 1

            l1_sum += abs(given % 3 - goal % 3) + abs(given // 3 - goal // 3)

        return l1_sum


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
        return self._heuristic.get(state, 0)


if __name__ == '__main__':
    a = ""
    print("==>", a)
