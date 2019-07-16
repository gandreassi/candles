#include <boost/range/irange.hpp>
# include <iostream>
#include <cmath>

void s_plot(){

	RooAbsData::setDefaultStorageType(RooAbsData::Tree);//this allows to use the tree() method to get a tre from the roodataset at the end

	TFile* f = TFile::Open("109E06BA-69D0-EE40-A601-60EBFFA53A8C.root");

	//Declare TTreeReader and the necessary variables
	TTreeReader r("Events", f);
	TTreeReaderValue<UInt_t> mus(r, "nMuon");
	TTreeReaderArray<Float_t> pt(r, "Muon_pt");
	TTreeReaderArray<Float_t> eta(r, "Muon_eta");
	TTreeReaderArray<Float_t> phi(r, "Muon_phi");
	TTreeReaderArray<Float_t> mass(r, "Muon_mass");
	TTreeReaderArray<Int_t> c(r, "Muon_charge");

	///RooFit stuff
	const float M_min =2.8;
	const float M_max =3.5;
	RooRealVar *M = new RooRealVar("M","m(#mu#mu)",M_min, M_max);
	RooRealVar *pt1 = new RooRealVar("mu1_pt","mu1_pt", -1);
	RooRealVar *pt2 = new RooRealVar("mu2_pt","mu2_pt", -1);
	RooDataSet *data = new RooDataSet("data", "data", RooArgSet(*M,*pt1,*pt2));


	//Loop on events...
	unsigned int max_evts=0;
	unsigned int i=0;

	while (r.Next()) {
		int c_prod=c[0]; //charge of the first muon
		int index_second_muon=-1;
		for (auto i : boost::irange(1,1+(int)*mus)){
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
				data->add(RooArgSet(*M, *pt1, *pt2));
			}
		}
		if (++i>max_evts and max_evts>0) break;
	}

	//Now we can create our pdf and fit it
	RooWorkspace w;
	w.import(*M);
	w.import(*data);
	w.factory("RooCBShape::cb(M,mu[3.05,3,3.2],sigma0[0.01,0.005,0.05], alpha[0.1,5],n[1,5])");
	w.factory("Gaussian::g1(M,mu,sigma1[0.07,0.01,0.15])");
	w.factory("Gaussian::g2(M,mu,sigma2[0.07,0.01,0.15])");
	w.factory("Gaussian::g3(M,mu,sigma3[0.01,0.005,0.1])");
	w.factory("SUM::sig(cb,gf1[0.3,0.1,1.0]*g1, gf2[0.3,0.1,1.0]*g2, gf3[0.3,0.1,1.0]*g3)");
	w.factory("Exponential::e(M,tau1[-1.5,-2,-0.01])");
	float nentries = data->sumEntries();
	RooRealVar s("s", "signal yield", 0.9*nentries, 0, nentries); //signal yield
	RooRealVar b("b", "background yield", 0.1*nentries, 0, nentries); //background yield
	w.import(s);
	w.import(b);
	w.factory("SUM::model(s*sig,b*e)");

	w.pdf("model")->fitTo(*data);


	auto frame = M->frame();
	TCanvas *canvas = new TCanvas("fit", "fit", 800, 600);
	data->plotOn(frame);
	w.pdf("model")->plotOn(frame);
	frame->Draw();


	RooStats::SPlot *sData = new RooStats::SPlot("sData", "An SPlot", *data, w.pdf("model"), RooArgList(s, b));

	RooTreeDataStore* store = (RooTreeDataStore*)data->store();
	TTree& reduced_tree = store->tree();
	RooArgList sweights = (RooArgList) sData->GetSWeightVars();

	TCanvas *canvas_sw = new TCanvas("c_sw", "c_sw", 800, 600);
	reduced_tree.Draw(M->GetName(), sweights[0].GetName());

	TFile* out_file = new TFile("reducedTree.root", "recreate");
	out_file->cd();
	reduced_tree.Write();
	out_file->Close();
	f->Close();
	exit(0);
}
