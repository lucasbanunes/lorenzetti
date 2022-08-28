#!/usr/bin/env python3

from GaugiKernel          import LoggingLevel, Logger
from GaugiKernel          import GeV
from P8Kernel             import EventReader
from G4Kernel             import *
from CaloCell.CaloDefs    import CaloSampling

import numpy as np
import argparse
import sys,os
MINUTES = 60

mainLogger = Logger.getModuleLogger("job")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()


parser.add_argument('-i','--inputFile', action='store', dest='inputFile', required = False,
                    help = "The event input file generated by the Pythia event generator.")

parser.add_argument('-o','--outputFile', action='store', dest='outputFile', required = False,
                    help = "The reconstructed event file generated by lzt/geant4 framework.")

parser.add_argument('-d', '--debug', action='store_true', dest='debug', required = False,
                    help = "In debug mode.")

parser.add_argument('-nt','--numberOfThreads', action='store', dest='numberOfThreads', required = False, type=int, default=1,
                    help = "The number of threads")

parser.add_argument('--evt','--numberOfEvents', action='store', dest='numberOfEvents', required = False, type=int, default=None,
                    help = "The number of events to apply the reconstruction.")

parser.add_argument('--visualization', action='store_true', dest='visualization', required = False,
                    help = "Run with Qt interface.")

parser.add_argument('--enableMagneticField', action='store_true', dest='enableMagneticField',required = False, 
                    help = "Enable the magnetic field.")

parser.add_argument('--outputLevel', action='store', dest='outputLevel', required = False, type=int, default=3,
                    help = "The output level messenger.")

parser.add_argument('-m','--merge', action='store_true', dest='merge', required = False, 
                    help = "Merge all output files.")

parser.add_argument('--saveAllHits', action='store_true', dest='saveAllHits', required = False, 
                    help = "Save all detector hits.")

parser.add_argument('-t','--timeout', action='store', dest='timeout', required = False, type=int, default=5,
                    help = "Event timeout in minutes")


pi = np.pi

if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()


outputLevel = 0 if args.debug else args.outputLevel

try:

  from DetectorATLASModel import DetectorConstruction as ATLAS
  from DetectorATLASModel import CaloHitBuilder
  
  
  # Build the ATLAS detector
  detector = ATLAS("GenericATLASDetector", 
                   UseMagneticField = args.enableMagneticField, # Force to be false since the mag field it is not working yet
                   #UseMagneticField = True,
                   UseDeadMaterial=True, # cause
                   # PS,EM1,EM2,EM3
                   UseBarrel=True,
                   # HAD1,2,3
                   UseTile=True,
                   # HAD1,2,3 ext.
                   UseTileExt=True,
                   # EMECs
                   UseEMEC= True,
                   # HECs
                   UseHEC = True, # cause
                   # crack region
                   UseCrack = True, # cause
                   CutOnPhi = False,
                   )
  

  acc = ComponentAccumulator("ComponentAccumulator", detector,
                              RunVis=args.visualization,
                              NumberOfThreads = args.numberOfThreads,
                              MergeOutputFiles = args.merge,
                              Seed = 512, # fixed seed since pythia will be used. The random must be in the pythia generation
                              OutputFile = args.outputFile,
                              Timeout = args.timeout * MINUTES )
  

  gun = EventReader( "PythiaGenerator",
                     EventKey   = recordable("EventInfo"),
                     TruthKey   = recordable("Particles"),
                     FileName   = args.inputFile,
                     BunchDuration = 25.0,#ns
                     )


  calorimeter_hits = CaloHitBuilder("CaloHitBuilder",
                                     HistogramPath = "Expert/Hits",
                                     OutputLevel   = outputLevel,
                                     )

  gun.merge(acc)
  calorimeter_hits.merge(acc)

  OutputHitsKey   = recordable("Hits")
  OutputEventKey  = recordable("EventInfo")

  from RootStreamBuilder import RootStreamHITMaker

  HIT = RootStreamHITMaker( "RootStreamHITMaker",
                             # input from context
                             InputHitsKey    = OutputHitsKey,
                             InputEventKey   = OutputEventKey,
                             InputTruthKey   = recordable("Particles"),
                             # output to file
                             OutputHitsKey   = recordable("Hits"),
                             OutputEventKey  = recordable("EventInfo"),
                             OutputTruthKey  = recordable("Particles"),
                             # special parameters
                             EtaWindow       = 0.6,
                             PhiWindow       = 0.6,
                             OnlyRoI         = not args.saveAllHits,
                             OutputLevel     = outputLevel)

  acc += HIT
  
  acc.run(args.numberOfEvents)
  
  
  if args.visualization:
      input("Press Enter to quit...")

  sys.exit(0)
  
except  Exception as e:
  print(e)
  sys.exit(1)
