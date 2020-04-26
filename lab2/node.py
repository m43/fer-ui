from clause import Clause


class Node:
    def __init__(self, expression):
        self.expression = expression
        expression = expression.strip() + " "
        bracket_counter = 0
        bracket_start = -1

        id_started = False
        id_start = -1

        self.state = 0
        self.operator = None

        self.left = None
        self.left_negated = False
        self.right = None
        self.right_negated = False

        for (i, c) in enumerate(expression):
            if bracket_counter == 0:
                if c == "~":
                    if self.state == 0:
                        self.left_negated = not self.left_negated
                    elif self.state == 1:
                        self.right_negated = not self.right_negated
                    else:
                        raise ValueError("Negation invalid.")
                elif c == "&":
                    if self.state != 1:
                        raise ValueError("Invalid position for &")
                    self._setOperator(c)
                elif c == "v":
                    if self.state != 1:
                        raise ValueError("Invalid position for v")
                    self._setOperator(c)
                elif c == ">":
                    if self.state != 1:
                        raise ValueError("Invalid position for >")
                    self._setOperator(c)
                elif c == "=":
                    if self.state != 1:
                        raise ValueError("Invalid position for =")
                    self._setOperator(c)
                elif c == " ":
                    if id_started:
                        id_started = False
                        if self.state == 0:
                            self.left = {frozenset([expression[id_start:i]])}
                            self.state += 1
                        elif self.state == 1:
                            self.right = {frozenset([expression[id_start:i]])}
                            self.state += 1
                        else:
                            raise ValueError("Parenthesis problem. Invalid problem")
                elif c == "(" or c == ")":
                    pass
                elif not id_started:
                    id_started = True
                    id_start = i

            if c == "(":
                if bracket_counter == 0:
                    bracket_start = i
                bracket_counter += 1
            elif c == ")":
                if bracket_counter == 1:
                    child = Node(expression[bracket_start + 1:i])
                    if self.state == 0:
                        self.left = child
                        self.state += 1
                    elif self.state == 1:
                        self.right = child
                        self.state += 1
                    else:
                        raise ValueError("Parenthesis problem. Invalid problem")
                bracket_counter -= 1

    def _setOperator(self, operator):
        if not self.operator:
            self.operator = operator
        else:
            raise ValueError("Operator already assign. Invalid format.")

    def evaluate(self):
        # return self._evaluate()
        result_clean = set()
        for clause in self._evaluate():
            if not Clause.cnf_tautology(clause) and clause != frozenset():
                result_clean.add(clause)

        if not result_clean:
            return {frozenset()}
        else:
            return result_clean

    def _evaluate(self):
        left_cnf = self.left.evaluate() if isinstance(self.left, Node) else self.left
        if self.left_negated:
            left_cnf = Clause.cnf_negated(left_cnf)

        if self.right is None:
            return left_cnf
        right_cnf = self.right.evaluate() if isinstance(self.right, Node) else self.right
        if self.right_negated:
            right_cnf = Clause.cnf_negated(right_cnf)

        if self.operator == "v":
            return Clause.disjunctionOperator(left_cnf, right_cnf)
        elif self.operator == "&":
            return Clause.conjunctionOperator(left_cnf, right_cnf)
        elif self.operator == "=":
            return Clause.equalityOperator(left_cnf, right_cnf)
        elif self.operator == ">":
            return Clause.implicationOperator(left_cnf, right_cnf)
        else:
            raise ValueError("Invalid operator! '{}'".format(self.operator))

    def __repr__(self):
        return self.expression

    @staticmethod
    def autocnf_from_file(filepath):
        output = []
        with open(filepath, "r+") as file:
            for line in file.read().splitlines():
                if line.startswith("#") or not line.strip():
                    continue
                cnf_format = Node(line).evaluate()
                output.append(Clause.clauses_to_string(cnf_format))
        return "\n".join(output)


if __name__ == "__main__":
    x = '~(C v D) v ((~A v F) & (J v O))'
    print(x)

    root = Node(x)
    root_cnf = root.evaluate()
    print(root_cnf)
    print(Clause.clauses_to_string(root_cnf))
