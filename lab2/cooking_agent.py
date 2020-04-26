from typing import List, Set
from clause import Clause
from resolution import Resolution


class CookingAgent:
    def __init__(self, facts: Set, debug: bool):
        self._knowledge = facts
        self._debug = debug

        if debug:
            print("Resolution system constructed with knowledge:")
            for clause in facts:
                print("> " + Clause.clause_to_string(clause))

    @staticmethod
    def parseCommand(line: str):
        parts = line.strip().rsplit(maxsplit=1)
        if len(parts) != 2:
            raise ValueError(
                'Given command "{}" is not of valid format.'.format(line))
        command = parts[1]
        clauses = Clause.parse_to_clauses(parts[0])
        if len(clauses) != 1:
            raise ValueError("Given command clause must be in CNF!")

        return tuple([clauses.pop(), command])

    def add_to_knowledge(self, clause: Set) -> bool:
        if clause in self._knowledge:
            return False

        self._knowledge.add(clause)
        return True

    def remove_from_knowledge(self, clause: Set) -> bool:
        if clause not in self._knowledge:
            return False

        self._knowledge.remove(clause)
        return True

    def query(self, clauses: Set) -> str:
        (proved, steps) = Resolution.check_deduction(self._knowledge, clauses, debug=self._debug)
        return steps

    def executeCommand(self, command):
        if command[1] == "?":
            print(self.query(command[0]))
        elif command[1] == "-":
            removed = self.remove_from_knowledge(command[0])
            if self._debug:
                if not removed:
                    print(Clause.clause_to_string(command[0]), "already removed")
                else:
                    print("removed", Clause.clause_to_string(command[0]))
        elif command[1] == "+":
            added = self.add_to_knowledge(command[0])
            if self._debug:
                if not added:
                    print(Clause.clause_to_string(command[0]), "already added")
                else:
                    print("added", Clause.clause_to_string(command[0]))
        else:
            raise ValueError('Command "' + str(command[1]) + '" is not recognized. Command found in:', str(command))

    def executeCommands(self, commands: List):
        for command in commands:
            self.executeCommand(command)

    def interactive(self):
        while True:
            line = input(">>> ").lower()
            try:
                command = self.parseCommand(line)
                if command[1] == "exit":
                    return
                self.executeCommand(command)
            except ValueError:
                print("Invalid command format")
