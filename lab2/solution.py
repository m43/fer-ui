#!/usr/bin/env python3

import sys

from cooking_agent import CookingAgent
from data_loader import Loader
from resolution import Resolution
from node import Node

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Program run without specific system arguments...")
        all_facts_list = Loader.load_facts("./resolution_examples/chicken_broccoli_alfredo_big.txt")
        last_fact = all_facts_list.pop()  # last fact is the goal
        print(Resolution.check_deduction(all_facts_list, last_fact, debug=True)[1])
        # ca = CookingAgent(set(Loader.load_facts("cooking_examples/chicken_alfredo.txt")), False)
        # ca.interactive()
        # ca.executeCommands(Loader.load_commands("cooking_examples/chicken_alfredo_input.txt"))
    elif sys.argv[1] == "resolution":
        all_facts_list = Loader.load_facts(sys.argv[2])
        last_fact = all_facts_list.pop()  # last fact is the goal
        debug = sys.argv[-1] == "verbose"
        print(Resolution.check_deduction(all_facts_list, last_fact, debug=debug)[1])
    elif sys.argv[1] == "cooking_test":
        facts_set = set(Loader.load_facts(sys.argv[2]))
        debug = sys.argv[-1] == "verbose"
        agent = CookingAgent(facts_set, debug)
        agent.executeCommands(Loader.load_commands(sys.argv[3]))
    elif sys.argv[1] == "cooking_interactive":
        facts_set = set(Loader.load_facts(sys.argv[2]))
        debug = sys.argv[-1] == "verbose"
        agent = CookingAgent(facts_set, debug)
        agent.interactive()
    elif sys.argv[1] == "smart_resolution_test":
        print("smart_resolution_test not implemented")
    elif sys.argv[1] == "smart_resolution_interactive":
        print("smart_resolution_interactive not implemented")
    elif sys.argv[1] == "autocnf":
        print(Node.autocnf_from_file(sys.argv[2]))
    else:
        print("Nothing to do here, got sysargs:", str(sys.argv))
