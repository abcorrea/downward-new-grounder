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
BENCHMARKS_DIR = os.environ["HTG_BENCHMARKS_FLATTENED"]
REVISIONS_AND_CONFIGS = [
    (
        ["old-grounder-v1"],
        [IssueConfig('lama', [], driver_options=['--alias', 'lama-first'])],
    ),
    (
        ["new-grounder-v1-lama"],
        [IssueConfig('lama', ['--translate-options', '--use-direct-lp-encoding'], driver_options=['--alias', 'lama-first'])],
    )
]

SUITE = ['blocksworld-large-simple',
         'childsnack-contents-parsize1-cham3',
         'childsnack-contents-parsize1-cham5',
         'childsnack-contents-parsize1-cham7',
         'childsnack-contents-parsize2-cham3',
         'childsnack-contents-parsize2-cham5',
         'childsnack-contents-parsize2-cham7',
         'childsnack-contents-parsize3-cham3',
         'childsnack-contents-parsize3-cham5',
         'childsnack-contents-parsize3-cham7',
         'childsnack-contents-parsize4-cham3',
         'childsnack-contents-parsize4-cham5',
         'childsnack-contents-parsize4-cham7',
         'genome-edit-distance',
         'genome-edit-distance-positional',
         'genome-edit-distance-split',
         'logistics-large-simple',
         'organic-synthesis-alkene',
         'organic-synthesis-MIT',
         'organic-synthesis-original',
        'pipesworld-tankage-nosplit',
         'rovers-large-simple',
         'visitall-multidimensional-3-dim-visitall-CLOSE-g1',
         'visitall-multidimensional-3-dim-visitall-CLOSE-g2',
         'visitall-multidimensional-3-dim-visitall-CLOSE-g3',
         'visitall-multidimensional-3-dim-visitall-FAR-g1',
         'visitall-multidimensional-3-dim-visitall-FAR-g2',
         'visitall-multidimensional-3-dim-visitall-FAR-g3',
         'visitall-multidimensional-4-dim-visitall-CLOSE-g1',
         'visitall-multidimensional-4-dim-visitall-CLOSE-g2',
         'visitall-multidimensional-4-dim-visitall-CLOSE-g3',
         'visitall-multidimensional-4-dim-visitall-FAR-g1',
         'visitall-multidimensional-4-dim-visitall-FAR-g2',
         'visitall-multidimensional-4-dim-visitall-FAR-g3',
         'visitall-multidimensional-5-dim-visitall-CLOSE-g1',
         'visitall-multidimensional-5-dim-visitall-CLOSE-g2',
         'visitall-multidimensional-5-dim-visitall-CLOSE-g3',
         'visitall-multidimensional-5-dim-visitall-FAR-g1',
         'visitall-multidimensional-5-dim-visitall-FAR-g2',
         'visitall-multidimensional-5-dim-visitall-FAR-g3']
ENVIRONMENT = BaselSlurmEnvironment(
    partition="infai_2",
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
    SUITE = ['genome-edit-distance:d-1-2.pddl']
    ENVIRONMENT = LocalEnvironment(processes=4)

exp = IssueExperiment(
    revisions_and_configs=REVISIONS_AND_CONFIGS,
    environment=ENVIRONMENT,
)
exp.add_suite(BENCHMARKS_DIR, SUITE)

exp.add_parser(exp.EXITCODE_PARSER)
exp.add_parser(exp.TRANSLATOR_PARSER)
exp.add_parser(exp.SINGLE_SEARCH_PARSER)
exp.add_parser(exp.PLANNER_PARSER)

exp.add_step('build', exp.build)
exp.add_step('start', exp.start_runs)
exp.add_fetcher(name='fetch')

exp.add_absolute_report_step(attributes=['translator_*']+exp.DEFAULT_TABLE_ATTRIBUTES)
exp.add_comparison_table_step(attributes=['translator_*']+exp.DEFAULT_TABLE_ATTRIBUTES)

exp.run_steps()
