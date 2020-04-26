import itertools
from clause import Clause


class Resolution:
    horizontal_line = "=" * 13 + "\n"

    @staticmethod
    def _refute_by_resolution(facts, goal) -> (bool, str):
        steps = ""
        clause_counter = 1
        clause_to_number = {}

        goal_negated = Clause.get_negated_clause(goal)

        clauses = set()
        clauses.update([x for x in facts if not Clause.cnf_tautology(x)])
        for clause in itertools.chain(facts, ["yolo"], goal_negated):
            if clause == "yolo":
                steps += Resolution.horizontal_line
                continue
            if clause not in clause_to_number:
                steps += "{}. {}\n".format(clause_counter, Clause.clause_to_string(clause))
                clause_to_number[clause] = clause_counter
                clause_counter += 1
        steps += Resolution.horizontal_line

        sos = set()
        sos_stage = set()
        sos_stage.update(goal_negated)
        sos_new = set()

        # TODO initial redundancy check (tautology check done, but not redundancy)

        while True:
            for (c1, c2) in itertools.chain(
                    itertools.product(sos_stage, sos_stage),
                    itertools.product(sos_stage, sos),
                    itertools.product(sos_stage, clauses)):
                if c1 == c2:
                    continue
                for resolvent in Clause.pl_resolve(c1, c2):
                    if resolvent and Clause.cnf_tautology(resolvent):
                        continue
                    # is_current_resolvent_a_subset = False
                    # for existing_clause in itertools.chain(sos, clauses, sos_new):
                    #     if resolvent.issubset(existing_clause):
                    #         is_current_resolvent_a_subset = True
                    #         break
                    #     elif existing_clause.issubset(resolvent):
                    #         if existing_clause in sos:
                    #             sos.remove(existing_clause)
                    #         elif existing_clause in clauses:
                    #             clauses.remove(existing_clause)
                    #         else:
                    #             sos_new.remove(existing_clause)
                    # if is_current_resolvent_a_subset:
                    #     break
                    if resolvent not in clause_to_number:
                        n1 = clause_to_number[c1]
                        n2 = clause_to_number[c2]
                        n1, n2 = (n2, n1) if (n1 > n2) else (n1, n2)
                        steps += "{}. {} ({}, {})\n".format(
                            clause_counter, Clause.clause_to_string(resolvent) if resolvent else "NIL", n1, n2)
                        clause_to_number[resolvent] = clause_counter
                        clause_counter += 1
                        sos_new.add(resolvent)
                    if not resolvent:
                        return tuple([True, steps])
            if not sos_new:
                if not clauses:
                    return tuple([False, steps])
                else:
                    clauses, sos_new = set(), clauses
            sos.update(sos_stage)
            sos_stage, sos_new = sos_new, set()

    @staticmethod
    def refute_by_resolution_proof(facts, goal) -> (bool, str):
        """
        Help method that tries to refute the given goal. The refutation is based on the knowledge given by facts.
        :param facts: knowledge aka the clauses that are to be considered true for this interpretation
        :param goal: the goal aka deduction that needs to be refuted
        :return: tuple(bool that is true if refutation succeeded, string describing with logical steps made)
        """
        (proved, steps) = Resolution._refute_by_resolution(facts, goal)
        steps += Resolution.horizontal_line
        steps += "refutation success" if proved else "refutation unsuccessful"
        return tuple([proved, steps])

    @staticmethod
    def check_deduction(facts, goal, debug: bool = False) -> (str, str):
        output = ""
        (prove_true, steps_true) = Resolution.refute_by_resolution_proof(facts, goal)
        if debug:
            output += steps_true + "\n\n"
        if prove_true:
            check_result = "true"
            return tuple([check_result, output + Clause.clause_to_string(goal) + " is " + check_result])

        (prove_false, steps_false) = Resolution.refute_by_resolution_proof(facts, goal)
        if debug:
            output += steps_false + "\n\n"

        check_result = "false" if prove_false else "unknown"
        return tuple([check_result, output + Clause.clause_to_string(goal) + " is " + check_result])
