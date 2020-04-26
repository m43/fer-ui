#!/usr/bin/env python3

import sys
from data_loader import Loader
from resolution import Resolution
from cooking_agent import CookingAgent

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("np")
        # all_facts_list = Loader.load_facts("./resolution_examples/chicken_alfredo.txt")
        # last_fact = all_facts_list.pop()  # last fact is the goal
        # print(Resolution.check_deduction(all_facts_list, last_fact, debug=True)[1])
        # ca = CookingAgent(Loader.load_facts("testeri-ijuren/cooking_examples/chicken_alfredo.txt"), False)
        # ca.executeCommands(Loader.load_commands("testeri-ijuren/cooking_examples/chicken_alfredo_input.txt"))
    elif sys.argv[1] == "resolution":
        all_facts_list = Loader.load_facts(sys.argv[2])
        last_fact = all_facts_list.pop()  # last fact is the goal
        print(Resolution.check_deduction(all_facts_list, last_fact, debug=False)[1])
    elif sys.argv[1] == "cooking_test":
        facts_set = set(Loader.load_facts(sys.argv[2]))
        if len(sys.argv) == 4:
            agent = CookingAgent(facts_set, False)
            agent.executeCommands(Loader.load_commands(sys.argv[3]))
        else:
            agent = CookingAgent(facts_set, True)
            agent.interactive()
    else:
        print("Nothing to do here, got sysargs:", str(sys.argv))
