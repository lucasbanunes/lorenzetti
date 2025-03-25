#!/usr/bin/env python3

import argparse
import sys
import os
from math import ceil
from typing import List
from joblib import Parallel, delayed
from evtgen import Pythia8
from filters import Zee

from GenKernel import EventTape
from GaugiKernel import get_argparser_formatter
from GaugiKernel import LoggingLevel
from GaugiKernel import GeV

PILEUP_FILE = os.environ['LZT_PATH'] + \
    '/generator/evtgen/data/minbias_config.cmnd'

ZEE_FILE = os.environ['LZT_PATH'] + \
    '/generator/evtgen/data/zee_config.cmnd'


def parse_args():

    parser = argparse.ArgumentParser(
        description='',
        formatter_class=get_argparser_formatter(),
        add_help=False)

    parser.add_argument('-e', '--event-numbers', action='store',
                        dest='event_numbers', required=False,
                        type=str, default=None,
                        help="The event number list separated "
                        "by ','. e.g. --event-numbers '0,1,2,3'")
    parser.add_argument('-o', '--output-file', action='store',
                        dest='output_file', required=True,
                        help="The event file generated by pythia.")
    parser.add_argument('--nov', '--number-of-events', action='store',
                        dest='number_of_events', required=False,
                        type=int, default=1,
                        help="The number of events to be generated.")
    parser.add_argument('--run-number', action='store',
                        dest='run_number', required=False,
                        type=int, default=0,
                        help="The run number.")
    parser.add_argument('-s', '--seed', action='store',
                        dest='seed', required=False,
                        type=int, default=0,
                        help="The pythia seed (zero is the clock system)")
    parser.add_argument('--output-level', action='store',
                        dest='output_level', required=False,
                        type=str, default="INFO",
                        help="The output level messenger.")
    parser.add_argument('--eta-max', action='store',
                        dest='eta_max', required=False,
                        type=float, default=3.2,
                        help="The eta max used in generator.")
    parser.add_argument('--force-forward-electron', action='store_true',
                        dest='force_forward_electron', required=False,
                        help="Force at least one electron "
                        "into forward region.")
    parser.add_argument('--zero-vertex-particles', action='store_true',
                        dest='zero_vertex_particles', required=False,
                        help="Fix the z vertex position in "
                        "simulation to zero for all selected particles. "
                        "It is applied only at G4 step, not in generation.")
    parser.add_argument('--pileup-avg', action='store',
                        dest='pileup_avg', required=False,
                        type=float, default=0,
                        help="The pileup average (default is zero).")
    parser.add_argument('--pileup-sigma', action='store',
                        dest='pileup_sigma', required=False,
                        type=float, default=0,
                        help="The pileup sigma (default is zero).")
    parser.add_argument('--bc-id-start', action='store',
                        dest='bc_id_start', required=False,
                        type=int, default=-21,
                        help="The bunch crossing id start.")
    parser.add_argument('--bc-id-end', action='store',
                        dest='bc_id_end', required=False,
                        type=int, default=4,
                        help="The bunch crossing id end.")
    parser.add_argument('--bc-duration', action='store',
                        dest='bc_duration', required=False,
                        type=int, default=25,
                        help="The bunch crossing duration (in nanoseconds).")
    parser.add_argument('-nt', '--number-of-threads', action='store',
                        dest='number_of_threads', required=False,
                        type=int, default=1,
                        help="The number of threads")
    parser.add_argument('--events-per-job', action='store',
                        dest='events_per_job', required=False,
                        type=int, default=None,
                        help="The number of events per job")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    return args


def main(events: List[int],
         logging_level: str,
         output_file: str,
         run_number: int,
         seed: int,
         zee_file: str,
         zero_vertex_particles: bool,
         force_forward_electron: bool,
         eta_max: float,
         pileup_avg: float,
         pileup_sigma: float,
         mb_file: str,
         bc_id_start: int,
         bc_id_end: int):

    outputLevel = LoggingLevel.toC(logging_level)

    tape = EventTape("EventTape", OutputFile=output_file,
                     RunNumber=run_number)

    zee = Zee("Zee",
              Pythia8("Generator",
                      File=zee_file,
                      Seed=args.seed),
              EtaMax=eta_max,
              MinPt=15*GeV,
              # calibration use only.
              ZeroVertexParticles=zero_vertex_particles,
              ForceForwardElectron=force_forward_electron,
              OutputLevel=outputLevel
              )
    tape += zee

    if args.pileup_avg > 0:

        from filters import Pileup
        pileup = Pileup("Pileup",
                        Pythia8("MBGenerator", File=mb_file,
                                Seed=seed),
                        EtaMax=eta_max,
                        Select=2,
                        PileupAvg=pileup_avg,
                        PileupSigma=pileup_sigma,
                        BunchIdStart=bc_id_start,
                        BunchIdEnd=bc_id_end,
                        OutputLevel=outputLevel,
                        DeltaEta=0.22,
                        DeltaPhi=0.22,
                        )

        tape += pileup
    tape.run(events)


def get_events_per_job(args):
    if args.events_per_job is None:
        return ceil(args.number_of_events/args.number_of_threads)
    else:
        return args.events_per_job


def get_job_params(args):
    if args.event_numbers:
        event_numbers_list = args.event_numbers.split(",")
        args.number_of_events = len(event_numbers_list)
        events_per_job = get_events_per_job(args)
        event_numbers = (
            event_numbers_list[start:start+events_per_job]
            for start in range(0, args.number_of_events, events_per_job)
        )
    else:
        events_per_job = get_events_per_job(args)
        event_numbers = (
            list(range(start, start+events_per_job))
            for start in range(0, args.number_of_events, events_per_job)
        )

    splitted_output_filename = args.output_file.split(".")
    for i, events in enumerate(event_numbers):
        output_file = splitted_output_filename.copy()
        output_file.insert(-1, str(i))
        output_file = '.'.join(output_file)
        if os.path.exists(output_file):
            print(f"{i} - Output file {output_file} already exists. Skipping.")
            continue
        yield events, output_file


if __name__ == "__main__":
    args = parse_args()
    pool = Parallel(n_jobs=args.number_of_threads)
    pool(delayed(main)(
        events=events,
        logging_level=args.output_level,
        output_file=output_file,
        run_number=args.run_number,
        seed=args.seed,
        zee_file=ZEE_FILE,
        zero_vertex_particles=args.zero_vertex_particles,
        force_forward_electron=args.force_forward_electron,
        eta_max=args.eta_max,
        pileup_avg=args.pileup_avg,
        pileup_sigma=args.pileup_sigma,
        mb_file=PILEUP_FILE,
        bc_id_start=args.bc_id_start,
        bc_id_end=args.bc_id_end
    )
        for events, output_file in get_job_params(args))
