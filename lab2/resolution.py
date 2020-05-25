import itertools
from clause import Clause


class Resolution:
    horizontal_line = "=" * 13 + "\n"

    clause_counter = 0

    @staticmethod
    def check_deduction(facts, goal_clause, debug: bool = False) -> (str, str):
        output = ""
        (prove_true, steps_true) = Resolution.refute_by_resolution_proof(facts, {goal_clause})
        if debug:
            output += steps_true + "\n\n"
        if prove_true:
            check_result = "true"
            return tuple([check_result, output + Clause.clause_to_string(goal_clause) + " is " + check_result])

        (prove_false, steps_false) = Resolution.refute_by_resolution_proof(facts,
                                                                           Clause.cnf_negated({goal_clause}))
        if debug:
            output += steps_false + "\n\n"

        check_result = "false" if prove_false else "unknown"
        return tuple([check_result, output + Clause.clause_to_string(goal_clause) + " is " + check_result])

    @staticmethod
    def refute_by_resolution_proof(facts, goal) -> (bool, str):
        """
        Help method that tries to refute the given goal. The refutation is based on the knowledge given by facts.
        :param facts: knowledge aka the clauses that are to be considered true for this interpretation
        :param goal: the goal set of clauses aka deduction that needs to be refuted
        :return: tuple(bool that is true if refutation succeeded, string describing with logical steps made)
        """
        (proved, steps) = Resolution._refute_by_resolution(facts, goal)
        steps += Resolution.horizontal_line
        steps += "refutation success" if proved else "refutation unsuccessful"
        return tuple([proved, steps])

    @staticmethod
    def _refute_by_resolution(facts, goal) -> (bool, str):
        steps = ""
        Resolution.clause_counter = 1
        clause_to_number = {}

        goal_negated = Clause.cnf_negated(goal)

        clauses = set()
        clauses.update([x for x in facts if not Clause.cnf_tautology(x)])
        for clause in itertools.chain(facts, ["yolo"], goal_negated):
            if clause == "yolo":
                steps += Resolution.horizontal_line
                continue
            if clause not in clause_to_number:
                steps += "{}. {}\n".format(Resolution.clause_counter, Clause.clause_to_string(clause))
                clause_to_number[clause] = Resolution.clause_counter
                Resolution.clause_counter += 1
        steps += Resolution.horizontal_line

        sos = set()
        sos_stage = set()
        sos_stage.update(goal_negated)
        sos_new = set()

        Clause.simplify_within_set_for_subsets(clauses)
        Clause.simplify_within_set_for_subsets(sos_stage)
        Clause.simplify_among_two_sets_for_subsets(sos_stage, clauses)

        while True:
            # # I'm sorry for this for loop. TODO refactor later
            # for (c1, c2) in itertools.product(sos_stage, sos_stage):
            #     x, steps = Resolution.__help_fun(c1, c2, sos_new, sos_stage, clauses, clause_to_number, steps)
            #     if x:
            #         return [x, steps]
            # if sos_new:
            #     sos_stage.update(sos_new)
            #     sos_new = set()
            #     continue
            #
            # for (c1, c2) in itertools.product(sos_stage, sos):
            #     x, steps = Resolution.__help_fun(c1, c2, sos_new, sos_stage, clauses, clause_to_number, steps)
            #     if x:
            #         return [x, steps]
            # if sos_new:
            #     sos_stage.update(sos_new)
            #     sos_new = set()
            #     continue
            #
            # for (c1, c2) in itertools.product(sos_stage, clauses):
            #     x, steps = Resolution.__help_fun(c1, c2, sos_new, sos_stage, clauses, clause_to_number, steps)
            #     if x:
            #         return [x, steps]
            # if not sos_new:
            #     if not clauses:
            #         return tuple([False, steps])
            #     else:
            #         clauses, sos_new = set(), clauses
            # sos.update(sos_stage)
            # sos_stage, sos_new = sos_new, set()

            for (c1, c2) in itertools.chain(
                    itertools.product(sos_stage, sos_stage),
                    itertools.product(sos_stage, sos),
                    itertools.product(sos_stage, clauses)):
                x, steps = Resolution.__help_fun(c1, c2, sos_new, sos_stage, clauses, clause_to_number, steps)
                if x:
                    return [x, steps]
            if not sos_new:
                # if not clauses:
                return tuple([False, steps])
                # else:
                #     clauses, sos_new = set(), clauses
            sos.update(sos_stage)
            sos_stage, sos_new = sos_new, set()

    @staticmethod
    def __help_fun(c1, c2, sos_new, sos_stage, clauses, clause_to_number, steps):
        # TODO refactor
        if c1 == c2:
            return [False, steps]
        for resolvent in Clause.pl_resolve(c1, c2):
            if resolvent and Clause.cnf_tautology(resolvent):
                continue
            if Clause.simplify_sets_by_clause_for_subsets(resolvent, sos_new, sos_stage, clauses):
                break
            if resolvent not in clause_to_number:
                n1 = clause_to_number[c1]
                n2 = clause_to_number[c2]
                n1, n2 = (n2, n1) if (n1 > n2) else (n1, n2)
                steps += "{}. {} ({}, {})\n".format(
                    Resolution.clause_counter, Clause.clause_to_string(resolvent) if resolvent else "NIL", n1, n2)
                clause_to_number[resolvent] = Resolution.clause_counter
                Resolution.clause_counter += 1
                sos_new.add(resolvent)
            if not resolvent:
                return tuple([True, steps])
        return [False, steps]
