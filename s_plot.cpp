#include <boost/range/irange.hpp>
# include <iostream>
#include <cmath>

void s_plot(){

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
	RooDataSet *data = new RooDataSet("data", "data", RooArgSet(*M));


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
				data->add(RooArgSet(*M));
			}
		}
		if (++i>max_evts and max_evts>0) break;
	}

	//Now we can create our pdf and fit it
	RooWorkspace w;
	w.import(*M);
	w.factory("RooCBShape::cb(M,mu[3.05,3,3.2],sigma0[0.01,0.005,0.05], alpha[0.1,5],n[1,5])");
	w.factory("Gaussian::g1(M,mu,sigma1[0.07,0.01,0.15])");
	w.factory("Gaussian::g2(M,mu,sigma2[0.07,0.01,0.15])");
	w.factory("Gaussian::g3(M,mu,sigma3[0.01,0.005,0.1])");
	w.factory("SUM::sig(cb,gf1[0.3,0.1,1.0]*g1, gf2[0.3,0.1,1.0]*g2, gf3[0.3,0.1,1.0]*g3)");
	w.factory("Exponential::e(M,tau1[-1.5,-2,-0.01])");
	w.factory("SUM::model(sig,b[0.2,0,0.6]*e)");

	w.pdf("model")->fitTo(*data);


	auto frame = M->frame();
	TCanvas *canvas = new TCanvas("canvas", "canvas", 800, 600);
	data->plotOn(frame);
	w.pdf("model")->plotOn(frame);
	frame->Draw();
	// exit(0);
}