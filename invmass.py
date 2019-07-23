#!/usr/bin/env python
import ROOT as r
r.gROOT.SetBatch(True)
r.PyConfig.IgnoreCommandLineOptions = True
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from libraries.getDataset import get_data
from importlib import import_module
from glob import glob
from sys import argv
import os
from math import floor

#call with "python invmass.py 'data/mc' 'year/file' 'dataset' 'particle'"

particle_range = {'jpsi': [2.5, 3.5], 'Y': [9.0, 10.0]}

class DiMuonMass(Module):
	def __init__(self):
		self.writeHistFile=True

	def beginJob(self,histFile=None,histDirName=None):
		Module.beginJob(self,histFile,histDirName)
		nbins = 100
		M_range = particle_range[argv[4]]
		self.M_max = M_range[1]
		self.M_min = M_range[0]
		binw = (self.M_max-self.M_min)/nbins
		self.hM = r.TH1F("hM", "DiMuon Mass", nbins, self.M_min, self.M_max)
		self.hM.GetXaxis().SetTitle("m(#mu#mu) [GeV/c^{2}]")
		self.hM.GetYaxis().SetTitle("Candidates / ("+str(binw)+"GeV/c^{2})")

		self.hM.SetMinimum(0)
		self.addObject(self.hM)

	def analyze(self, event):
		muons = Collection(event, "Muon")
		eventSum = r.TLorentzVector()

		#select events with at least 2 muons, opposite charge
		mu_plus = filter(lambda x: x.charge==1, muons)
		mu_minus = filter(lambda x: x.charge==-1, muons)
		
		
		eventSum = mu_plus[0].p4()+mu_minus[0].p4()
		M = eventSum.M()
		if (self.M_min<=M<=self.M_max):
			self.hM.Fill(eventSum.M())
			return True
		else: return False

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from libraries.getDataset import get_T3_data_files
dset = "ZeroBias"
year = "2018"
#l=glob("/store/data/Run2018D/ZeroBias/NANOAOD/Nano14Dec2018_ver2-v1/90000/E1FE45EC-FB3D-C747-80D8-462D0833DD2B.root")

#data, l = get_data("ZeroBias", "2018")
#data, l = get_data("SingleMuon", "2018")
# data, l = get_data("Charmonium", "2018")
#print l
#from MuOnia import l
from Charmonium import l
l.sort()
print l
print argv
low = int(floor((int(argv[5])-1)*float(len(l))/int(argv[6])))
high = int(floor((int(argv[5])*float(len(l))/int(argv[6]))-1))
print low, high
l=l[low:high]

cut="Sum$(Muon_charge>0)>0 && Sum$(Muon_charge<0)>0 && HLT_Dimuon0_LowMass"#&& (HLT_Dimuon0_LowMass)"# && (HLT_Mu3_PFJet40 || HLT_Dimuon0_Jpsi3p5_Muon2 || HLT_Dimuon0_Jpsi_L1_4R_0er1p5R || HLT_Dimuon0_Jpsi_L1_NoOS ||\
#HLT_Dimuon0_Jpsi_NoVertexing_L1_4R_0er1p5R || HLT_Dimuon0_Jpsi_NoVertexing_NoOS || HLT_Dimuon0_Jpsi_NoVertexing || HLT_Dimuon0_Jpsi || HLT_Dimuon0_LowMass_L1_0er1p5R ||\
#HLT_Dimuon0_LowMass_L1_0er1p5 || HLT_Dimuon0_LowMass_L1_4R || HLT_Dimuon0_LowMass_L1_4 || HLT_Dimuon0_LowMass)"

p=PostProcessor("/home/gandreas/jpsi_project/CMSSW_10_2_9/src/skimmed/",l,cut=cut,branchsel="/home/gandreas/jpsi_project/CMSSW_10_2_9/src/keep_and_drop.txt",modules=[DiMuonMass()],histFileName="/home/gandreas/jpsi_project/CMSSW_10_2_9/src/tm/hM"+argv[5]+".root",histDirName="hists", noOut=False) #noOut prevents from writing cut tree to disk
p.run()
