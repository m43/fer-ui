from typing import List
from cooking_agent import CookingAgent
from clause import Clause


class Loader:
    @staticmethod
    def load_facts(filepath) -> List:
        _clauses = []
        with open(filepath, "r+") as file:
            for line in file.read().splitlines():
                if line.startswith("#") or not line.strip():
                    continue
                _clauses.extend(Clause.parse_to_clauses(line.strip()))
        return _clauses

    @staticmethod
    def load_commands(filepath) -> List:
        _commands = []
        with open(filepath, "r+") as file:
            for line in file.read().splitlines():
                if line.startswith("#") or not line.strip():
                    continue
                _commands.append(CookingAgent.parseCommand(line))
        return _commands
