#!/usr/bin/env python
# coding: utf-8


import ROOT as r
from ROOT import RooFit as rf
import numpy as np
from ROOT import RooStats as rs

f = r.TFile.Open("hists/jpsi_close.root")
h = f.Get("hists/hM")
f2 = r.TFile.Open("muon_hists.root")
tree = r.TTree()
f2.GetObject("Events;1", tree)
Muon_mass = r.RooRealVar("Muon_mass","Muon_mass",2.85,3.5)
Muon_pt = r.RooRealVar("Muon_pt", "Muon_pt",0,100)
data = r.RooDataSet("data", "data", tree, r.RooSetArg(Muon_mass, Muon_pt))

w = r.RooWorkspace()
x = w.factory('M[2.85,3.5]')
w.factory('RooCBShape::cb(M,mu[3.05,3,3.2],sigma0[0.01,0.005,0.05], alpha[0.1,5],n[1,5])')
w.factory('Gaussian::g1(M,mu,sigma1[0.07,0.01,0.15])')
w.factory('Gaussian::g2(M,mu,sigma2[0.07,0.01,0.15])')
w.factory('Gaussian::g3(M,mu,sigma3[0.01,0.005,0.1])')
w.factory('SUM::sig(cb,gf1[0.3,0.1,1.0]*g1, gf2[0.3,0.1,1.0]*g2, gf3[0.3,0.1,1.0]*g3)')
w.factory('Exponential::e(M,tau1[-1.5,-2,-0.01])')
w.factory('SUM::model(sig,b[0.2,0,0.6]*e)')


h_roofit = r.RooDataHist("h", "h", r.RooArgList(x), h)
w.pdf("model").fitTo(h_roofit)

#import data
getattr(w,'import')(h, 'hist')
getattr(w,'import')(data, 'data')


def getS_weights(w):
    #w: workshop with variables, data and pdf model

    num_events = w.genobj('hist').GetEntries()
    model = w.pdf('model')
    b = w.var('b')
    
    data = w.genobj('data')
    #print(data)

    #yields
    N_bkrd = b.getVal() * num_events
    N_sig = num_events - N_bkrd
    print(N_sig, num_events)
    
    '''
    #fixing paramters
    print(w.var('M'))
    '''
    sData = rs.SPlot("sData", "An SPlot", data, model, r.RooArgList())

    '''
    inv_cov_mat = np.empty([2,2])
    for i in range(2):
        for j in range(2):
            val = 0  
            
            while var:
                varlist.append(var.GetName())
                var = iter_set.Next()
                inv_cov_mat[i][j] = val
                ...
    return True
    '''

getS_weights(w)

'''
mframe = x.frame()
mframe.SetTitle("")
h_roofit.plotOn(mframe)
w.pdf("model").plotOn(mframe)
hpull = mframe.pullHist()
w.pdf("model").plotOn(mframe, rf.Components("e"), rf.LineColor(r.kRed))
w.pdf("model").plotOn(mframe, rf.Components("sig"), rf.LineColor(r.kGreen))

mframe.GetXaxis().SetTitleSize(0)
mframe.GetXaxis().SetLabelSize(0)
pframe = x.frame()
pframe.SetTitle("")
pframe.GetXaxis().SetLabelSize(0.1)
pframe.GetXaxis().SetTitle("m(#mu#mu)")
pframe.GetXaxis().SetTitleSize(0.15)
pframe.GetYaxis().SetLabelSize(0.1)
pframe.GetYaxis().SetTitle("Pool  ")
pframe.GetYaxis().SetTitleSize(0.15)
pframe.GetYaxis().SetTitleOffset(0.3)
pframe.addPlotable(hpull,"P")

c = r.TCanvas("c","c",800,600)

pad1 = r.TPad("pad1", "pad1",0,0.25,1,1)
pad1.SetBottomMargin(0.02)
pad1.cd()
mframe.Draw()

pad2 = r.TPad("pad2", "pad2",0,0,1,0.25)
pad2.SetTopMargin(0.05)
pad2.SetBottomMargin(0.4)
pad2.cd()
pframe.Draw()

c.cd()
pad1.Draw()
pad2.Draw()
c.Draw()
c.SaveAs("jpsi.pdf")



'''
