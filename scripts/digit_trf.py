#!/usr/bin/env python3

from GaugiKernel          import LoggingLevel, Logger
from GaugiKernel          import GeV
from CaloCell.CaloDefs    import CaloSampling
from G4Kernel.utilities   import *
import numpy as np
import argparse
import sys,os

import ROOT
ROOT.gSystem.Load('liblorenzetti')
from ROOT import RunManager

mainLogger = Logger.getModuleLogger("job")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()


parser.add_argument('-i','--inputFile', action='store', dest='inputFile', required = False,
                    help = "The event input file generated by the Pythia event generator.")

parser.add_argument('-o','--outputFile', action='store', dest='outputFile', required = False,
                    help = "The reconstructed event file generated by lzt/geant4 framework.")

parser.add_argument('-d', '--debug', action='store_true', dest='debug', required = False,
                    help = "In debug mode.")

parser.add_argument('--evt','--numberOfEvents', action='store', dest='numberOfEvents', required = False, type=int, default=-1,
                    help = "The number of events to apply the reconstruction.")

parser.add_argument('--outputLevel', action='store', dest='outputLevel', required = False, type=int, default=3,
                    help = "The output level messenger.")



pi = np.pi

if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()


outputLevel = 0 if args.debug else args.outputLevel

try:

  from GaugiKernel import ComponentAccumulator
  acc = ComponentAccumulator("ComponentAccumulator", args.outputFile)


  # the reader must be first in sequence
  from RootStreamBuilder import RootStreamHITReader
  reader = RootStreamHITReader("HITReader", 
                                InputFile       = args.inputFile,
                                HitsKey         = recordable("Hits"),
                                EventKey        = recordable("EventInfo"),
                                TruthKey        = recordable("Particles"),
                                NtupleName      = "CollectionTree",
                              )


  reader.merge(acc)

  # digitalization!
  from DetectorATLASModel import CaloCellBuilder
  calorimeter = CaloCellBuilder("CaloCellBuilder",
                                HistogramPath = "Expert/Cells",
                                OutputLevel   = outputLevel,
                                HitsKey       = recordable("Hits"),
                                )
  calorimeter.merge(acc)


  from RootStreamBuilder import RootStreamESDMaker
  ESD = RootStreamESDMaker( "RootStreamESDMaker",
                             InputCellsKey   = recordable("Cells"),
                             InputEventKey   = recordable("EventInfo"),
                             InputTruthKey   = recordable("Particles"),
                             OutputCellsKey  = recordable("Cells"),
                             OutputEventKey  = recordable("EventInfo"),
                             OutputTruthKey  = recordable("Particles"),            
                             NtupleName      = "CollectionTree",
                             OutputLevel     = outputLevel)
  acc += ESD
  

  acc.run(args.numberOfEvents)

  
  sys.exit(0)
  
except Exception as e:
  print(e)
  sys.exit(1)
