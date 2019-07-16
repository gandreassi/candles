import ROOT as r
r.gROOT.SetBatch(True)
r.PyConfig.IgnoreCommandLineOptions = True
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from libraries.getDataset import get_data_chain
from importlib import import_module
from glob import glob
from sys import argv
import os

#call with "python invmass.py 'data/mc' 'year/file' 'dataset' 'particle'"

particle_range = {'jpsi': [2.85, 3.5], 'Y': [9.0, 10.0]}

class DiMuonMass(Module):
	def __init__(self):
		self.writeHistFile=True

	def beginJob(self,histFile=None,histDirName=None):
		Module.beginJob(self,histFile,histDirName)
		nbins = 100
		M_range = particle_range[argv[4]]
		M_max = M_range[1]
		M_min = M_range[0]
		binw = (M_max-M_min)/nbins
		self.hM = r.TH1F("hM", "DiMuon Mass", nbins, M_min, M_max)
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
		

		self.hM.Fill(eventSum.M())

		return True

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor

#path = "/mnt/hadoop/cms/store/"+argv[1]+"/"+argv[2]+"/"+argv[3]
#l = [os.path.join(dirpath, f) for dirpath, dirnames, files in os.walk(path)
#     for f in files if f.endswith('.root')]
#print(l)

#l=glob("/mnt/hadoop/cms/store/"+argv[1]+"/*"+argv[2]+"*/"+argv[3]+"/**/*.root", recursive=True)
l=glob("/mnt/hadoop/cms/store/"+argv[1]+"/*"+argv[2]+"*/"+argv[3]+"/*/*/*/*.root")
#l=glob("/mnt/hadoop/cms/store/data/Run2018A/MuOnia/NANOAOD/Nano14Dec2018-v1/20000/10A2B17F-D56F-1A40-B663-835364230D30.root")

cut="Sum$(Muon_charge>0)>0 && Sum$(Muon_charge<0)>0" #requesting at least a positive and a negative muon in each event
p=PostProcessor(".",l,cut,branchsel="keep_and_drop.txt",modules=[DiMuonMass()],histFileName="hM.root",histDirName="hists", noOut=True) #noOut prevents from writing cut tree to disk
p.run()
