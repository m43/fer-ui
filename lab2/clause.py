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

    @staticmethod
    def simplify_within_set_for_subsets(clauses_set) -> None:
        for clause in list(clauses_set):
            to_remove = set()
            if clause in clauses_set:
                for other in clauses_set:
                    if other != clause and clause.issubset(other):
                        to_remove.add(other)
            clauses_set -= to_remove

    @staticmethod
    def simplify_among_two_sets_for_subsets(clauses_set_1, clauses_set_2) -> None:
        """
        Simplifies the given two sets among each other, looking if one has a clause that is a subset of the other.
        Subsets will then get removed. Given sets must be simplified within themselves, otherwise the function will not
        work properly.

        :param clauses_set_1: first set of clauses
        :param clauses_set_2: second set of clauses
        """
        to_remove = set()
        for clause in clauses_set_1:
            if Clause.simplify_sets_by_clause_for_subsets(clause, clauses_set_2):
                to_remove.add(clause)

    @staticmethod
    def simplify_sets_by_clause_for_subsets(clause, *old_clauses_sets) -> bool:
        for clauses in old_clauses_sets:
            to_remove = set()
            for existing_clause in clauses:
                if existing_clause != clause:
                    if existing_clause.issubset(clause):
                        return True
                    elif clause.issubset(existing_clause):
                        to_remove.add(existing_clause)
                        # print("#Subsumption:", Clause.clause_to_string(existing_clause), "subsummed by",
                        #       Clause.clause_to_string(clause))
            clauses -= to_remove
