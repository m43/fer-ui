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
    def cnf_negated(clauses: Set) -> Set:
        """
        Returns the set of clauses that are the result of negating this CNF set.

        This is how it does the trick:
        a v b
        ~c
        d v f

        negated(^) --> (~a & ~b) v (c) v (~d & ~f)
          --> {}
          --> {{~a}, {~b}}
          --> {{~a,c}, {~b,c}}
          --> {{~a,c,~d}, {~b,c,~d}, {~a,c,~f}, {~b,c,~f}}

        :param clauses: the clauses in CNF format
        :return: the negated clauses in CNF format
        """
        negated = [set()]
        for clause in clauses:
            next_negated = []
            negated_clause = [Clause.get_negated_literal(x) for x in clause]
            for x in negated_clause:
                for y in negated:
                    current = y.copy()
                    current.add(x)
                    next_negated.append(current)

            negated = next_negated

        negated_frozen = set([frozenset(x) for x in negated])
        return negated_frozen

    @staticmethod
    def get_negated_literal(literal: str) -> str:
        if literal.startswith("~"):
            return literal[1:]
        else:
            return "~" + literal

    @staticmethod
    def clause_to_string(clause: Set) -> str:
        return " v ".join(clause)
