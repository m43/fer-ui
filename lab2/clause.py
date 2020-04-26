from typing import Set, List


class Clause:
    @staticmethod
    def parse_to_clauses(string: str) -> List:
        return [frozenset([x.strip() for x in string.lower().split(" v ")])]

    @staticmethod
    def cnf_tautology(clause):
        for x in clause:
            if Clause.get_negated_literal(x) in clause:
                return True
        return False

    @staticmethod
    def pl_resolve(c1, c2):
        for x in c1:
            x_neg = Clause.get_negated_literal(x)
            if x_neg in c2:
                resolvent = set()
                resolvent.update(c1, c2)
                resolvent.remove(x)
                resolvent.remove(x_neg)
                yield frozenset(resolvent)  # TODO how to freeze set directly

    @staticmethod
    def get_negated_clause(clause: Set) -> Set:
        negated = set()
        for x in clause:
            negated.add(frozenset([Clause.get_negated_literal(x)]))
        return negated

    @staticmethod
    def get_negated_literal(literal: str) -> str:
        if literal.startswith("~"):
            return literal[1:]
        else:
            return "~" + literal

    @staticmethod
    def clause_to_string(clause: Set) -> str:
        return " v ".join(clause)
