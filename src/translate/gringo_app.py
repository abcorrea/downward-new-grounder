import sys
import re

import clingo
from clingo.control import Control
from clingox.program import Program, ProgramObserver, Remapping

import pddl
import timers

import networkx as nx

class ClingoApp(object):
    def __init__(self, name, no_show=False, ground_guess=False, ground=False, map_actions=dict()):
        self.program_name = name
        self.sub_doms = {}
        self.no_show = no_show
        self.ground_guess = ground_guess
        self.ground = ground
        self.map_actions = map_actions

        self.relevant_atoms = []
        self.prg = Program()

    def main(self, ctl, files):
        ctl_insts = Control()
        ctl_insts.register_observer(ProgramObserver(self.prg))
        # read subdomains in #program insts.
        self._readSubDoms(ctl_insts,files)

        if self.ground:
            for f in self.prg.facts:
                name = f.symbol.name
                if name.startswith("temp__") or name.startswith("equals"):
                    pass
                if name.startswith('action_'):
                    # if it is an action predicate, then predicate is the object
                    predicate = self.map_actions[str(name)]
                else:
                    # if it is not an action, than predicate is a simple string
                    for rep in (('___xx___', '@'), ('__', '-')):
                        name = name.replace(*rep)
                    predicate = name
                args = []
                for a in f.symbol.arguments:
                    args.append(a.name)

                self.relevant_atoms.append(pddl.Atom(predicate, tuple(args)))

        print("Size of the model:", len(self.prg.facts))
        print("Number of atoms (not actions): %d" % len(self.relevant_atoms))

    def _readSubDoms(self, ctl_insts, files):
        #ctl_insts = Control()
        print("Loading theory files...")
        for f in files:
            ctl_insts.load(f)
        print("Theory files loaded!")
        with timers.timing("Computing model..."):
            ctl_insts.ground([("base", []), ("insts", [])])
        for k in ctl_insts.symbolic_atoms:
            if(str(k.symbol).startswith('_dom_')):
                var = str(k.symbol).split("(", 1)[0]
                atom = re.sub(r'^.*?\(', '', str(k.symbol))[:-1]
                _addToSubdom(self.sub_doms, var, atom)

def _addToSubdom(sub_doms, var, value):
    if var.startswith('_dom_'):
        var = var[5:]
    else:
        return

    if var not in sub_doms:
        sub_doms[var] = []
        sub_doms[var].append(value)
    elif value not in sub_doms[var]:
        sub_doms[var].append(value)


def main(files, map_actions):
    no_show = False
    ground_guess = True
    ground = True

    clingo_app = ClingoApp(sys.argv[0], no_show, ground_guess, ground, map_actions)

    clingo.clingo_main(clingo_app, files)
    return clingo_app.relevant_atoms
