#!/usr/bin/env python3
from GaugiKernel   import LoggingLevel, Logger
from GaugiKernel   import GeV
import argparse
import sys,os


mainLogger = Logger.getModuleLogger("pythia")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

#
# Mandatory arguments
#


parser.add_argument('-o','--outputFile', action='store', dest='outputFile', required = True,
                    help = "The event file generated by pythia.")

parser.add_argument('--nov','--numberOfEvents', action='store', dest='numberOfEvents', required = False, type=int, default=1,
                    help = "The number of events to be generated.")

parser.add_argument('--event_number', action='store', dest='event_number', 
                    required = False, default=[], type=int,
                    help = "The list of numbers per event.")

#
# Pileup simulation arguments
#

parser.add_argument('--pileupAvg', action='store', dest='pileupAvg', required = False, type=int, default=40,
                    help = "The pileup average (default is zero).")

parser.add_argument('--bc_id_start', action='store', dest='bc_id_start', required = False, type=int, default=-21,
                    help = "The bunch crossing id start.")

parser.add_argument('--bc_id_end', action='store', dest='bc_id_end', required = False, type=int, default=4,
                    help = "The bunch crossing id end.")

parser.add_argument('--bc_duration', action='store', dest='bc_duration', required = False, type=int, default=25,
                    help = "The bunch crossing duration (in nanoseconds).")


#
# Extra parameters
#

parser.add_argument('--outputLevel', action='store', dest='outputLevel', required = False, type=int, default=0,
                    help = "The output level messenger.")

parser.add_argument('-s','--seed', action='store', dest='seed', required = False, type=int, default=0,
                    help = "The pythia seed (zero is the clock system)")

parser.add_argument('--maxEta', action='store', dest='maxEta', required = False, type=float, default=3.2,
                    help = "Maximum eta coordinate")

parser.add_argument('--energy_min', action='store', dest='energy_min', required = False, type=float, default=17,
                    help = "Maximum eta coordinate")


if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()


try:


  minbias_file = os.environ['LZT_PATH']+'/generator/guns/data/minbias_config.cmnd'
  main_file    = os.environ['LZT_PATH']+'/generator/guns/data/jet_config.cmnd'
  
  from guns import P8Gun
  from GenKernel import EventTape
  from filters import JF17

  tape = EventTape( "EventTape", OutputFile = args.outputFile)
  
  
  # To collect using this cell position
  jets = JF17( "JF17",
               #SherpaGun("Generator", File=main_file, Seed=args.seed)
               PythiaGun("MainGenerator", File=main_file, Seed=args.seed, EventNumber = args.event_number),
               EtaMax      = args.maxEta,
               MinPt       = args.energy_min*GeV,
               Select      = 2,
               EtaWindow   = 0.4,
               PhiWindow   = 0.4,
               OutputLevel = args.outputLevel,
              )
  
  # generate jets
  tape+=jets

  if args.pileupAvg > 0:

    from filters import Pileup
    
    pileup = Pileup( "MinimumBias",
                   PythiaGun("MBGenerator", File=minbias_file, Seed=args.seed),
                   EtaMax         = args.maxEta,
                   Select         = 2,
                   PileupAvg      = args.pileupAvg,
                   BunchIdStart   = args.bc_id_start,
                   BunchIdEnd     = args.bc_id_end,
                   OutputLevel    = args.outputLevel,
                   DeltaEta       = 0.22,
                   DeltaPhi       = 0.22,
                   )
    # Add pileup
    tape+=pileup


  # Run!
  tape.run(args.numberOfEvents)

  sys.exit(0)
except  Exception as e:
  print(e)
  sys.exit(1)