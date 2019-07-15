import ROOT as r
r.gROOT.SetBatch(True)
r.PyConfig.IgnoreCommandLineOptions = True
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class TriggerExplore(Module):
	def __init__(self, lines):
		self.writeHistFile=True
		self.triggers=lines

	def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
		tr = inputTree.GetListOfBranches()
		tr = [t.GetName() for t in tr]
		self.this_files_triggers = [t for t in tr if t[:3]=="HLT"]


	def beginJob(self,histFile=None,histDirName=None):
		Module.beginJob(self,histFile,histDirName)
		self.hTs = r.THStack("stack", "Main HLT lines")
		self.addObject(self.hTs)
		#make histograms
		nbins = 170
		M_max = 11
		M_min = 2.5
		self.binw = (M_max-M_min)/nbins
		self.hT={}
		for i, t in enumerate(self.triggers):
			self.hT[t] = r.TH1F(t, t, nbins, M_min, M_max)
			self.addObject(self.hT[t])

	def analyze(self, event):
		muons = Collection(event, "Muon")
		eventSum = r.TLorentzVector()

		#select events with at least 2 muons, opposite charge
		mu_plus = filter(lambda x: x.charge==1, muons)
		mu_minus = filter(lambda x: x.charge==-1, muons)
		eventSum = mu_plus[0].p4()+mu_minus[0].p4()

		for tr in self.triggers:
			if tr in self.this_files_triggers:
				if getattr(event, tr):
					self.hT[tr].Fill(eventSum.M())

		return True

	def endJob(self):
		for h in self.hT.itervalues():
			print h
			self.hTs.Add(h)

		c = r.TCanvas("c", "c", 500,300)
		self.hTs.Draw("pfc")
		self.hTs.GetXaxis().SetTitle("m(#mu#mu) [GeV/c^{2}]")
		self.hTs.GetYaxis().SetTitle("Candidates / ("+str(self.binw)+"GeV/c^{2})")
		self.hTs.SetMinimum(0)
		c.Modified()
		r.gPad.BuildLegend(0.32,0.65,0.68,0.9,"")
		c.SaveAs("plots/triggers_{dset}_{year}.pdf".format(dset=dset, year=year))


#control sequence
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from libraries.getDataset import get_T3_data_files
dset = "MuOnia"
year = "2018"
l=get_T3_data_files(dset, year)
cut="Sum$(Muon_charge>0)>0 && Sum$(Muon_charge<0)>0" #requesting at least a positive and a negative muon in each event
lines = ["HLT_Dimuon10_Upsilon_Barrel_Seagulls",
		"HLT_Dimuon14_Phi_Barrel_Seagulls",
		"HLT_Dimuon12_Upsilon_y1p4",
		"HLT_Dimuon12_Upsilon_eta1p5",
		"HLT_Dimuon24_Upsilon_noCorrL1",
		"HLT_L2Mu23NoVtx_2Cha",
		"HLT_L2Mu23NoVtx_2Cha_CosmicSeed"]
p=PostProcessor(".",l,cut=cut,branchsel="keep_and_drop_trigger.txt",modules=[TriggerExplore(lines)],histFileName="hT_{dset}_{year}.root".format(dset=dset, year=year),histDirName="hists", noOut=True) #noOut prevents from writing cut tree to disk
p.run()

