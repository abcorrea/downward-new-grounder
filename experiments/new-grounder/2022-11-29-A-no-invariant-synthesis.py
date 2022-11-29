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

from cactus import CactusPlotReport

DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
BENCHMARKS_DIR = os.environ["HTG_BENCHMARKS_FLATTENED"]
REVISIONS_AND_CONFIGS = [
    (
        ["old-grounder-v1"],
        [IssueConfig('lama',
                     ['--translate-options', '--invariant-generation-max-candidates', '0'],
                     driver_options=['--alias', 'lama-first',
                                     '--overall-time-limit',
                                     '60m',
                                     '--overall-memory-limit',
                                     '3872M'])],
    ),
    (
        ["new-grounder-v1-lama"],
        [IssueConfig('lama',
                     ['--translate-options', '--use-direct-lp-encoding', '--invariant-generation-max-candidates', '0'],
                     driver_options=['--alias', 'lama-first',
                                     '--overall-time-limit',
                                     '60m',
                                     '--overall-memory-limit',
                                     '3872M'])],
    ),
    (
        ["new-grounder-v2-fix"],
        [IssueConfig('lama',
                     ['--translate-options', '--use-direct-lp-encoding', '--invariant-generation-max-candidates', '0'],
                     driver_options=['--alias', 'lama-first',
                                     '--overall-time-limit',
                                     '60m',
                                     '--overall-memory-limit',
                                     '3872M'])],
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
    partition="infai_1",
    export=["PATH", "HTG_BENCHMARKS_FLATTENED"]
)

if common_setup.is_test_run():
    SUITE = ['genome-edit-distance:d-2-1.pddl']
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

def combine_larger_domains(run):
    if 'childsnack-contents-parsize' in run['domain']:
        run['problem'] = '{}-{}'.format(run['domain'], run['problem'])
        run['domain'] = 'childsnacks-large'
        return run
    if 'visitall-multidimensional' in run['domain']:
        run['problem'] = '{}-{}'.format(run['domain'], run['problem'])
        run['domain'] = 'visitall-multidimensional'
        return run
    if 'genome-edit-distance' in run['domain']:
        run['problem'] = '{}-{}'.format(run['domain'], run['problem'])
        run['domain'] = 'genome-edit-distance'
        return run
    if 'organic-synthesis-' in run['domain']:
        run['problem'] = '{}-{}'.format(run['domain'], run['problem'])
        run['domain'] = 'organic-synthesis'
        return run
    return run


exp.add_absolute_report_step(attributes=['translator_*']+exp.DEFAULT_TABLE_ATTRIBUTES+['planner_wall_clock_time'],
                             filter=[combine_larger_domains])

exp.add_comparison_table_step(attributes=['translator_*']+exp.DEFAULT_TABLE_ATTRIBUTES)

exp.add_report(CactusPlotReport(filter_algorithm=['new-grounder-v2-fix-lama']),
               name="cactus")


exp.run_steps()
