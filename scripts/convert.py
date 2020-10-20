



from Gaugi import Logger
from Gaugi import ToolSvc
from Gaugi import Algorithm
from Gaugi import StatusCode
from Gaugi import save
from Gaugi.messenger import LoggingLevel
from Gaugi.messenger.macros import *
from G4Kernel import CaloPhiRange
import numpy as np
from CaloCell import CaloLayer

_caloPhiRange = CaloPhiRange()


# Use this converter for ATLAS simulation only
class Convert( Algorithm ):

  def __init__(self, name,  outputname):
    Algorithm.__init__(self, name)
    self._outputname  = outputname
    self._event = []


  def initialize(self):
  
    self._event_label = ['avgmu']
    self._event_label.extend( [ 'ring_%d'%r for r in range(100) ] )
    self._event_label.extend( [ 
                                'et',
                                'eta',
                                'phi',
                                'eratio',
                                'reta',
                                'rphi',
                                'rhad',
                                'f1',
                                'f3',
                                'weta2',
                                'ehad1',
                                'ehad2',
                                'ehad3',
                                ] )

    self._cells =  {
        'ps'   : [],
        'em1'  : [],
        'em2'  : [],
        'em3'  : [],
        'had1' : [],
        'had2' : [],
        'had3' : [],
        }


    return StatusCode.SUCCESS


  def fill( self, event ):
    self._event.append(event)


  def execute(self, context):
    
    event = self.getContext().getHandler( "EventInfoContainer" )
    cluster = self.getContext().getHandler( "CaloClusterContainer" )
    ringer = cluster.caloRings()
    
    if cluster.isValid() and ringer.isValid():
    
      event_row = list() 
      event_row.append( event.avgmu() )
      event_row.extend( ringer.ringsE() )
      event_row.append( cluster.et() )
      event_row.append( cluster.eta() )
      event_row.append( cluster.phi() )
      event_row.append( cluster.eratio() )
      event_row.append( cluster.reta() )
      event_row.append( cluster.rphi() )
      event_row.append( cluster.rhad() )
      event_row.append( cluster.f1() )
      event_row.append( cluster.f3() )
      event_row.append( cluster.weta2() )
      event_row.append( cluster.ehad1() )
      event_row.append( cluster.ehad2() )
      event_row.append( cluster.ehad3() )

      self._cells['ps'].append( self.reshapeCells( cluster, CaloLayer.PS ) )
      self._cells['em1'].append( self.reshapeCells( cluster, CaloLayer.EM1 ) )
      self._cells['em2'].append( self.reshapeCells( cluster, CaloLayer.EM2 ) )
      self._cells['em3'].append( self.reshapeCells( cluster, CaloLayer.EM3 ) )
      self._cells['had1'].append( self.reshapeCells( cluster, CaloLayer.HAD1 ) )
      self._cells['had2'].append( self.reshapeCells( cluster, CaloLayer.HAD2 ) )
      self._cells['had3'].append( self.reshapeCells( cluster, CaloLayer.HAD3 ) )
    

      # Fill the event
      self.fill(event_row)
 

    return StatusCode.SUCCESS
  

  def finalize( self ):

    d = { "features"   : self._event_label ,
          "data"       : np.array( self._event ),
          "cells_ps"   : np.array(self._cells['ps']),
          "cells_em1"  : np.array(self._cells['em1']),
          "cells_em2"  : np.array(self._cells['em2']),
          "cells_em3"  : np.array(self._cells['em3']),
          "cells_had1" : np.array(self._cells['had1']),
          "cells_had2" : np.array(self._cells['had2']),
          "cells_had3" : np.array(self._cells['had3']),
        }


    save( d, self._outputname, protocol = 'savez_compressed', )
    return StatusCode.SUCCESS

  def reshapeCells(self, cluster , sampling):

    # get all cells for this specific layer
    cells = cluster.getCells( sampling )

    hotCell = None
    frame = np.zeros( (501, 501) ) # center in 250, 250

    # Build the frame 
    for cell in cells:
      i = 250 + round((_caloPhiRange.diff(cell.phi(), cluster.phi())) / cell.deltaPhi())
      j = 250 + round((cell.eta() - cluster.eta()) / cell.deltaEta())
      frame[i][j] = cell.energy() 

    # Crop the frame for ATLAS detector definition only
    from CaloCell import CaloLayer    
    if sampling is CaloLayer.PS:
      neta = 6; nphi = 1
    elif sampling is CaloLayer.EM1:
      neta = 42; nphi = 1
    elif sampling is CaloLayer.EM2:
      neta = 6; nphi = 6
    elif sampling is CaloLayer.EM3:
      neta = 3; nphi = 6
    elif sampling is CaloLayer.HAD1:
      neta = 2; nphi = 1
    elif sampling is CaloLayer.HAD2:
      neta = 2; nphi = 1
    elif sampling is CaloLayer.HAD3:
      neta = 1; nphi = 1
    frame = frame[   (250 - nphi):(250 + nphi+1) ,(250 - neta):(250 + neta+1) ] 
    
    return frame









import argparse
import sys,os


mainLogger = Logger.getModuleLogger("job")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()


parser.add_argument('-i','--inputFile', action='store', dest='inputFile', required = True, nargs='+',
                    help = "The event input file generated by the reco simulator.")

parser.add_argument('-o','--outputfile', action='store', dest='outputFile', required = True,
                    help = "the numpy file.")

parser.add_argument('-n','--nov', action='store', dest='nov', required = False, default=-1, type=int,
                    help = "the numpy file.")


if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()



from GaugiKernel import EventReader
from GaugiKernel.enumerations import Dataframe as DataframeEnum

acc = EventReader("EventLorenzettLoop",
                  inputFiles = args.inputFile, 
                  treePath = 'physics', 
                  dataframe = DataframeEnum.Lorenzetti_v1, 
                  outputFile = args.outputFile,
                  level = LoggingLevel.INFO )


ToolSvc += Convert( "ConvertToPyObject" , args.outputFile)

# Run it!
acc.run(args.nov)



