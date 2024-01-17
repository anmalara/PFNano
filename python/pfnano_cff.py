import FWCore.ParameterSet.Config as cms
from PhysicsTools.PFNano.addPFCands_cff import addPFCands
from PhysicsTools.NanoAOD.common_cff import Var


def PFnano_customizeMC(process):
    addPFCands(process, runOnMC=True)
    return process


def PFnano_customizeData(process):
    addPFCands(process, runOnMC=False)
    return process
