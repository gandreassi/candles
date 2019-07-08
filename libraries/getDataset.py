#author: Guido Andreassi <guido.andreassi@cern.ch>
#These functions help retrieving the CMS data for the Bmm analysis

import itertools, collections
import subprocess, ast, json
import ROOT as r

def get_data(dset, year, version="Nano14Dec2018"):
	print "Retrieving", dset, "data for year", year, "..."
	q = "file dataset=/{dset}*/Run{year}*-{version}*/NANOAOD".format(dset=dset, year=year, version=version)
	out = subprocess.Popen(['dasgoclient', '-query', q, '-json'], 
	           stdout=subprocess.PIPE, 
	           stderr=subprocess.STDOUT)
	stdout,stderr = out.communicate()
	data = json.loads(stdout)
	data_files = ["root://cms-xrd-global.cern.ch/"+d["file"][0]["name"] for d in data]
	return data, data_files

def get_data_chain(dset, year):
	data, data_files = get_data(dset, year)
	data_files=data_files[:2]
	print data_files
	c = r.TChain("Events")
	for f in data_files:
		c.Add(f)
	return c

def get_all_ana_data():
	years = ["2017", "2018"]
	dsets = ["MuOnia", "Charmonium"]
	data = collections.defaultdict(dict) #full dictionary with all info on data
	data_files = collections.defaultdict(dict) #dictionary of files

	for dset, year in itertools.product(dsets, years):
		return get_data(dset, year)


