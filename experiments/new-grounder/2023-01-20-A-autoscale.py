#! /usr/bin/env pypy3

import itertools
import math
import os
import subprocess

from lab.environments import LocalEnvironment, BaselSlurmEnvironment
from lab.reports import Attribute

from downward.reports.compare import ComparativeReport

import common_setup
from common_setup import IssueConfig, IssueExperiment

DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
BENCHMARKS_DIR = os.environ["AUTOSCALE_BENCHMARKS_SAT"]
REVISIONS_AND_CONFIGS = [
    (
        ["old-grounder-v1"],
        [IssueConfig('translate', [], driver_options=['--translate',
                                                      '--overall-memory-limit', '8G'])],
    ),
    (
        ["new-grounder-clingo"],
        [IssueConfig('translate', ['--translate-options', '--use-direct-lp-encoding'],
                     driver_options=['--translate',
                                     '--overall-memory-limit', '8G'])],
    )
]

SUITE = ["agricola",
         "airport",
         "barman",
         "blocksworld",
         "childsnack",
         "data-network",
         "depots",
         "driverlog",
         "elevators",
         "floortile",
         "freecell",
         "ged",
         "grid",
         "gripper",
         "hiking",
         "logistics",
         "miconic",
         "mprime",
         "nomystery",
         "openstacks",
         "organic-synthesis-split",
         "parcprinter",
         "parking",
         "pathways",
         "pegsol",
         "pipesworld-notankage",
         "pipesworld-tankage",
         "rovers",
         "satellite",
         "scanalyzer",
         "snake",
         "sokoban",
         "storage",
         "termes",
         "tetris",
         "thoughtful",
         "tidybot",
         "tpp",
         "transport",
         "visitall",
         "woodworking",
         "zenotravel"]

ENVIRONMENT = BaselSlurmEnvironment(
    partition="infai_2",
    memory_per_cpu="6GB",
    cpus_per_task=2,
    export=[],
    # paths obtained via:
    # module purge
    # module -q load CMake/3.15.3-GCCcore-8.3.0
    # module -q load GCC/8.3.0
    # echo $PATH
    # echo $LD_LIBRARY_PATH
#    setup='export PATH=/scicore/soft/apps/binutils/2.32-GCCcore-8.3.0/bin:/scicore/soft/apps/CMake/3.15.3-GCCcore-8.3.0/bin:/scicore/soft/apps/cURL/7.66.0-GCCcore-8.3.0/bin:/scicore/soft/apps/bzip2/1.0.8-GCCcore-8.3.0/bin:/scicore/soft/apps/ncurses/6.1-GCCcore-8.3.0/bin:/scicore/soft/apps/GCCcore/8.3.0/bin:/infai/roeger/bin:/infai/roeger/local/bin:/export/soft/lua_lmod/centos7/lmod/lmod/libexec:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:$PATH\nexport LD_LIBRARY_PATH=/scicore/soft/apps/binutils/2.32-GCCcore-8.3.0/lib:/scicore/soft/apps/cURL/7.66.0-GCCcore-8.3.0/lib:/scicore/soft/apps/bzip2/1.0.8-GCCcore-8.3.0/lib:/scicore/soft/apps/zlib/1.2.11-GCCcore-8.3.0/lib:/scicore/soft/apps/ncurses/6.1-GCCcore-8.3.0/lib:/scicore/soft/apps/GCCcore/8.3.0/lib64:/scicore/soft/apps/GCCcore/8.3.0/lib',
)

if common_setup.is_test_run():
    SUITE = ['zenotravel:p01.pddl']
    ENVIRONMENT = LocalEnvironment(processes=4)

exp = IssueExperiment(
    revisions_and_configs=REVISIONS_AND_CONFIGS,
    environment=ENVIRONMENT,
)
exp.add_suite(BENCHMARKS_DIR, SUITE)

exp.add_parser(exp.EXITCODE_PARSER)
exp.add_parser(exp.TRANSLATOR_PARSER)

exp.add_step('build', exp.build)
exp.add_step('start', exp.start_runs)
exp.add_fetcher(name='fetch')

exp.add_absolute_report_step(attributes=['translator_*', 'error', 'run_dir'])
exp.add_comparison_table_step(attributes=['translator_*', 'error', 'run_dir'])

exp.run_steps()
