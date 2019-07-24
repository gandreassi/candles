#include <iostream>
#include <cmath>
#include "RooAbsData.h"
#include "TChain.h"
#include "TTreeReader.h"
#include "TTreeReaderArray.h"
#include "RooRealVar.h"
#include "RooDataSet.h"
#include "TLorentzVector.h"
#include "TCanvas.h"
#include "RooWorkspace.h"
#include "RooAbsPdf.h"
#include "RooPlot.h"
#include "RooStats/SPlot.h"
#include "RooTreeDataStore.h"
#include "TFile.h"
#include "TAxis.h"
#include "TPad.h"

void s_plot(){

	RooAbsData::setDefaultStorageType(RooAbsData::Tree);//this allows to use the tree() method to get a tree from the roodataset at the end

	TChain* chain = new TChain("Events");
	chain->Add("/mnt/hadoop/scratch/gandreas/Charmonium_Dimuon0_LowMass_skimmed/*.root");
	//chain->Add("/mnt/hadoop/scratch/gandreas/Charmonium_Dimuon0_LowMass_skimmed/09403A9F-B753-EC40-AA01-3C8CA976F23E_Skim.root");   (for testing)

	//Declare TTreeReader and the necessary variables
	TTreeReader r(chain);
	TTreeReaderValue<UInt_t> mus(r, "nMuon");
	TTreeReaderArray<Float_t> pt(r, "Muon_pt");
	TTreeReaderArray<Float_t> eta(r, "Muon_eta");
	TTreeReaderArray<Float_t> phi(r, "Muon_phi");
	TTreeReaderArray<Float_t> mass(r, "Muon_mass");
	TTreeReaderArray<Int_t> c(r, "Muon_charge");

	///RooFit stuff
	const float M_min =2.5;
	const float M_max =3.5;
	RooRealVar *M = new RooRealVar("M","m(#mu#mu)",M_min, M_max);
	RooRealVar *pt1 = new RooRealVar("mu1_pt","mu1_pt", -1);
	RooRealVar *pt2 = new RooRealVar("mu2_pt","mu2_pt", -1);
	RooRealVar *eta1 = new RooRealVar("mu1_eta","mu1_eta", -1);
	RooRealVar *eta2 = new RooRealVar("mu2_eta","mu2_eta", -1);
	RooRealVar *dlt_phi = new RooRealVar("dlt_phi","dlt_phi", -1);
	RooRealVar *nMuon = new RooRealVar("nMuon","nMuon", -1);
	RooDataSet *data = new RooDataSet("data", "data", RooArgSet(*M,*pt1,*pt2,*eta1,*eta2,*dlt_phi,*nMuon));


	//Loop on events...
	unsigned int max_evts=0;
	unsigned int i=0;

	while (r.Next()) {
		int c_prod=c[0]; //charge of the first muon
		int index_second_muon=-1;
		for (int i=1; i<(int)*mus; i++){
			if (c_prod*c[i]==-1){//opposite charge requirement. That"s going to be our second muon
				index_second_muon=i;
				break;
			}
		}

		if (index_second_muon>0){

			TLorentzVector P1;
			TLorentzVector P2;
			P1.SetPtEtaPhiM(pt[0], eta[0], phi[0], mass[0]);
			P2.SetPtEtaPhiM(pt[index_second_muon], eta[index_second_muon], phi[index_second_muon], mass[index_second_muon]);
			TLorentzVector P = P1+P2;

			///add RooDataSet
			float DiMuon_mass=P.M();
			if (DiMuon_mass>=M_min && DiMuon_mass<=M_max){
				*M=DiMuon_mass;
				*pt1=pt[0];
				*pt2=pt[index_second_muon];
				*eta1=eta[0];
				*eta2=eta[index_second_muon];
				//getting signed delta phi of muons (pos-neg) and adjusting for pi, -pi split
				float temp_dlt_phi=(phi[0]-phi[index_second_muon])*c[0];
				if (abs(temp_dlt_phi)>M_PI){
				  if (temp_dlt_phi>0){
				    temp_dlt_phi=temp_dlt_phi-2*M_PI;
				  }
				  else {
				    temp_dlt_phi=temp_dlt_phi+2*M_PI;
				  }
				}
				*dlt_phi=temp_dlt_phi;
				*nMuon=(int)*mus;
				data->add(RooArgSet(*M, *pt1, *pt2, *eta1, *eta2, *dlt_phi, *nMuon));
			}
		}
		if (++i>max_evts and max_evts>0) break;
	}

	//Now we can create our pdf and fit it
	RooWorkspace w;
	w.import(*M);
	w.import(*data);
	w.factory("RooCBShape::cb(M,mu[3.05,3,3.2],sigma0[0.01,0.005,0.05], alpha[0.1,3],n[1,5])");
	w.factory("Gaussian::g1(M,mu,sigma1[0.07,0.01,0.15])");
	w.factory("Gaussian::g2(M,mu,sigma2[0.07,0.01,0.15])");
	///w.factory("Gaussian::g3(M,mu,sigma3[0.01,0.005,0.1])");
	w.factory("SUM::sig(cb,gf1[0.3,0.1,1.0]*g1, gf2[0.3,0.01,1.0]*g2)");
	w.factory("Exponential::e(M,tau1[-2,-3,-0.1])");
	float nentries = data->sumEntries();
	RooRealVar s("s", "signal yield", 0.9*nentries, 0, nentries); //signal yield
	RooRealVar b("b", "background yield", 0.1*nentries, 0, nentries); //background yield
	w.import(s);
	w.import(b);
	w.factory("SUM::model(s*sig,b*e)");

	w.pdf("model")->fitTo(*data);


	auto frame = M->frame();
	frame->SetTitle("");
	data->plotOn(frame);
	w.pdf("model")->plotOn(frame);
	auto hpull = frame->pullHist();
	w.pdf("model")->plotOn(frame, RooFit::Components("e"), RooFit::LineColor(kRed), RooFit::LineStyle(kDashed));
	w.pdf("model")->plotOn(frame, RooFit::Components("sig"), RooFit::LineColor(kGreen), RooFit::LineStyle(kDashed));

	frame->GetXaxis()->SetTitleSize(0);
	frame->GetXaxis()->SetLabelSize(0);
	auto pframe = M->frame();
	pframe->SetTitle("");
	pframe->GetXaxis()->SetLabelSize(0.1);
	pframe->GetXaxis()->SetTitle("m(#mu#mu)");
	pframe->GetXaxis()->SetTitleSize(0.15);
	pframe->GetYaxis()->SetLabelSize(0.1);
	pframe->GetYaxis()->SetTitle("Pool  ");
	pframe->GetYaxis()->SetTitleSize(0.15);
	pframe->GetYaxis()->SetTitleOffset(0.3);
	pframe->addPlotable(hpull,"P");

	TCanvas *canvas = new TCanvas("fit", "fit", 800, 600);;

	TPad* pad1 = new TPad("pad1", "pad1",0,0.25,1,1);
	pad1->SetBottomMargin(0.02);
	pad1->cd();
	frame->Draw();

	TPad* pad2 = new TPad("pad2", "pad2",0,0,1,0.25);
	pad2->SetTopMargin(0.05);
	pad2->SetBottomMargin(0.4);
	pad2->cd();
	pframe->Draw();

	canvas->cd();
	pad1->Draw();
	pad2->Draw();
	canvas->Draw();
	canvas->SaveAs("plots/s_fit.pdf");


	RooStats::SPlot *sData = new RooStats::SPlot("sData", "An SPlot", *data, w.pdf("model"), RooArgList(s, b));

	RooTreeDataStore* store = (RooTreeDataStore*)data->store();
	TTree& reduced_tree = store->tree();
	RooArgList sweights = (RooArgList) sData->GetSWeightVars();

	TCanvas *canvas_sw = new TCanvas("c_sw", "c_sw", 800, 600);
	reduced_tree.Draw(M->GetName(), sweights[0].GetName());
	canvas_sw->SaveAs("plots/sw_sig.pdf");

	TFile* out_file = new TFile("reducedTree.root", "recreate");
	out_file->cd();
	reduced_tree.Write();
	out_file->Close();
	exit(0);
}
