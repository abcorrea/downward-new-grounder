import sys
import re

import clingo
from clingo.control import Control
from clingox.program import Program, ProgramObserver, Remapping

import networkx as nx

class ClingoApp(object):
    def __init__(self, name, no_show=False, ground_guess=False, ground=False):
        self.program_name = name
        self.sub_doms = {}
        self.no_show = no_show
        self.ground_guess = ground_guess
        self.ground = ground

        self.relevant_atoms = []
        self.prg = Program()

    def main(self, ctl, files):
        ctl_insts = Control()
        ctl_insts.register_observer(ProgramObserver(self.prg))
        # read subdomains in #program insts.
        self._readSubDoms(ctl_insts,files)
        list_atoms = []
        atoms = 0
        if self.ground:
            for f in self.prg.facts:
                fact = f.symbol
                if not str(fact).startswith("temp__") and not str(fact).startswith("equals"):
                    # count everything which is not temporary and build-int
                    atoms = atoms + 1
                    self.relevant_atoms.append(f)


        print("Size of the model:", len(self.prg.facts))
        print("Number of atoms (not actions): %d" % atoms)

    def _readSubDoms(self, ctl_insts, files):
        #ctl_insts = Control()
        for f in files:
            ctl_insts.load(f)
        ctl_insts.ground([("base", []), ("insts", [])])
        print("Grounding done!")
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


def main(files):
    no_show = False
    ground_guess = True
    ground = True

    clingo_app = ClingoApp(sys.argv[0], no_show, ground_guess, ground)

    clingo.clingo_main(clingo_app, files)
    return clingo_app.relevant_atoms