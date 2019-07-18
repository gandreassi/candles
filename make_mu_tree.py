#!/usr/bin/env python
# coding: utf-8

import ROOT as r
from glob import glob
import sys

#call with python make_mu_tree.py 'data/mc' 'year/file' 'dataset'

#ch = r.TChain("Events")
l = glob("/mnt/hadoop/cms/store/"+sys.argv[1]+"/*"+sys.argv[2]+"*/"+sys.argv[3]+"/*/*/*/*.root")

num_files = len(l)
i = 0
for f in sorted(l):
    i+=1
    #get only muon branches
    oldfile = r.TFile.Open(f)
    oldtree = r.TTree()
    oldfile.GetObject("Events", oldtree)
    oldtree.SetBranchStatus("*", 0)
    oldtree.SetBranchStatus("Muon*", 1)
    newfile = r.TFile.Open("temp_muons.root", "UPDATE")
    newtree = oldtree.CloneTree(0)
    newtree.CopyEntries(oldtree)
    newfile.Write()

    #ch.Add('temp_muons.root')

    newfile.Close("R")
    #print(str(ch.GetEntries())+" Events")
    print(str(float(i)/float(num_files)*100) + '% done...')

print('Tree Completed!')
#print(str(ch.GetEntries())+" Events")

'''
ch = r.TChain("Events")
treelist = r.TList()
l = glob("/mnt/hadoop/cms/store/"+sys.argv[1]+"/*"+sys.argv[2]+"*/"+sys.argv[3]+"/*/*/*/*.root")

num_files = len(l)
i = 0
for f in l:
    print(str(float(i)/float(num_files)*100) + '% done...')
    
    oldfile = r.TFile.Open(f)
    
    oldtree = r.TTree()
    oldfile.GetObject("Events", oldtree)

    #keeping only muon branches active
    oldtree.SetBranchStatus("*", 0)
    oldtree.SetBranchStatus("Muon*", 1)
    
    treelist.Add(oldtree.CloneTree())
    
    ch.Add(f)
    i+=1

#finaltree = r.TTree.MergeTrees(treelist)

#finaltree.Browse(TBrowser())


#make new muon branch file
#newfile = r.TFile.Open('muon_branch.root', 'RECREATE')
print()
'''
