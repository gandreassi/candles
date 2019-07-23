CXX=g++
CXXFLAGS=-O3 -fPIC -Wall

ROOT_FLAGS=$(shell $(ROOTSYS)/bin/root-config --cflags)
ROOT_INCLUDE=-I$(shell $(ROOTSYS)/bin/root-config  --incdir)

BUILDDIR=.
OBJ_DIR=.

INCLUDE=-I$(INCLUDEEPDIR) -I$(ROOT_INCLUDE) -I$(ROOFIT_INCLUDE) -I$(BOOST)/include

ROOT_LIBS    = $(shell $(ROOTSYS)/bin/root-config --libs) -lTreePlayer -lMinuit -lXMLIO -lMLP -lRIO -lTMVA 
GLIBS := $(shell root-config --glibs)
FLAGS = $(CXXFLAGS)
FLAGS += ${ROOT_FLAGS}
FLAGS_ROOFIT = $(FLAGS)
FLAGS_ROOFIT += -lRooFitCore -lRooFit -lRooStats -lFoam


MACRO=s_plot

all: $(MACRO)

$(MACRO): main.cpp
	@echo "---> Making s_plot..."
	$(CXX) $(CXXFLAGS) $(GLIBS) $(FLAGS_ROOFIT) $(ROOT_LIBS) -I $(INCLUDE) $^ -o $(MACRO).exe


clean:
	rm -f $(BUILDDIR)/$(MACRO).exe
