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
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]
REVISIONS_AND_CONFIGS = [
    (
        ["old-grounder-v1"],
        [IssueConfig('lama', [],
                     driver_options=['--alias', 'lama-first',
                                     '--overall-memory-limit',
                                     '16G'])],
    ),
    (
        ["new-grounder-v1-lama"],
        [IssueConfig('lama',
                     ['--translate-options', '--use-direct-lp-encoding'],
                     driver_options=['--alias', 'lama-first',
                                     '--overall-memory-limit',
                                     '16G'])],
    )
]

SUITE = common_setup.DEFAULT_SATISFICING_SUITE
ENVIRONMENT = BaselSlurmEnvironment(
    partition="infai_2",
    memory_per_cpu="6G",
    extra_options='#SBATCH --cpus-per-task=3',
    export=["PATH", "DOWNWARD_BENCHMARKS"]
)

if common_setup.is_test_run():
    SUITE = IssueExperiment.DEFAULT_TEST_SUITE
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
