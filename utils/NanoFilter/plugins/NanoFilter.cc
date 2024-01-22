// -*- C++ -*-
//
// Package:    PhysicsTools/NanoFilter
// Class:      NanoFilter
//
/**\class NanoFilter NanoFilter.cc PhysicsTools/NanoFilter/plugins/NanoFilter.cc

 Description: Apply selection to filter events based on VBF H->inv

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Andrea Malara
//         Created:  Thu, 18 Jan 2024 17:31:06 GMT
//
//

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDFilter.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/MET.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/PatCandidates/interface/Photon.h"

//
// class declaration
//

class NanoFilter : public edm::stream::EDFilter<> {
public:
  explicit NanoFilter(const edm::ParameterSet&);
  ~NanoFilter();

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void beginStream(edm::StreamID) override;
  bool filter(edm::Event&, const edm::EventSetup&) override;
  void endStream() override;

  bool hasElectrons(edm::Event&);
  bool hasMuons(edm::Event&);
  bool hasPhotons(edm::Event&);

  //void beginRun(edm::Run const&, edm::EventSetup const&) override;
  //void endRun(edm::Run const&, edm::EventSetup const&) override;
  //void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
  //void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;

  // ----------member data ---------------------------
// Physics object tokens
  edm::EDGetTokenT<edm::View<pat::Jet>> jetToken_;
  edm::EDGetTokenT<edm::View<pat::MET>> metToken_;
  edm::EDGetTokenT<edm::View<pat::Muon>> muonToken_;
  edm::EDGetTokenT<edm::View<pat::Electron>> electronToken_;
  edm::EDGetTokenT<edm::View<pat::Photon>> photonToken_;  
  // Pt thresholds for each object
  double metPtThresh_;
  unsigned int nJetMinThresh_;
  double jetPtThresh_;
  double electronPtThresh_;
  double muonPtThresh_;
  double photonPtThresh_;
};

//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
NanoFilter::NanoFilter(const edm::ParameterSet& iConfig) {
  jetToken_ = consumes<edm::View<pat::Jet>>(iConfig.getParameter<edm::InputTag>("jets"));
  metToken_ = consumes<edm::View<pat::MET>>(iConfig.getParameter<edm::InputTag>("met"));
  muonToken_ = consumes<edm::View<pat::Muon>>(iConfig.getParameter<edm::InputTag>("muons"));
  electronToken_ = consumes<edm::View<pat::Electron>>(iConfig.getParameter<edm::InputTag>("electrons"));
  photonToken_ = consumes<edm::View<pat::Photon>>(iConfig.getParameter<edm::InputTag>("photons"));
  metPtThresh_ = iConfig.getParameter<double>("metPtMin");
  nJetMinThresh_  = iConfig.getParameter<unsigned int>("nJetMin");
  jetPtThresh_ = iConfig.getParameter<double>("jetPtMin");
  electronPtThresh_ = iConfig.getParameter<double>("electronPtMin");
  muonPtThresh_ = iConfig.getParameter<double>("muonPtMin");
  photonPtThresh_ = iConfig.getParameter<double>("photonPtMin");
}

NanoFilter::~NanoFilter() {
  // do anything here that needs to be done at destruction time
  // (e.g. close files, deallocate resources etc.)
  //
  // please remove this method altogether if it would be left empty
}

//
// member functions
//

bool NanoFilter::hasElectrons(edm::Event& iEvent) {
  /*
  Returns True if a loose electron is found in the event.
  */
  edm::Handle<edm::View<pat::Electron>> electrons;
  iEvent.getByToken(electronToken_, electrons);
  for (const auto &e : *electrons) {
    // Compute cut based ID
    int32_t cutBasedIDVeto = e.userInt("cutBasedID_Fall17V2_veto");
    int32_t cutBasedIDLoose = e.userInt("cutBasedID_Fall17V2_loose");
    int32_t cutBasedIDMedium = e.userInt("cutBasedID_Fall17V2_medium");
    int32_t cutBasedIDTight = e.userInt("cutBasedID_Fall17V2_tight");

    int32_t cutBasedId = cutBasedIDVeto + cutBasedIDLoose + cutBasedIDMedium + cutBasedIDTight;
    if ((e.pt() > electronPtThresh_) && (cutBasedId > 0)) { 
      return true; 
    }
  }
  return false;
}

bool NanoFilter::hasMuons(edm::Event& iEvent) {
  /*
   Returns True if a loose & isolated muon within a certain pt 
   threshold is found in the event.
  */
  edm::Handle<edm::View<pat::Muon>> muons;
  iEvent.getByToken(muonToken_, muons);
  for (const auto &m : *muons) {
    // Compute isolation for this muon
    double chHadPt = m.pfIsolationR04().sumChargedHadronPt;
    double neHadEt = m.pfIsolationR04().sumNeutralHadronEt;
    double phoEt = m.pfIsolationR04().sumPhotonEt;
    double sumPUPt = m.pfIsolationR04().sumPUPt;
    double pfRelIso = (chHadPt + std::max<double>(0.0, neHadEt + phoEt - 0.5 * sumPUPt)) / m.pt();

    if ((m.pt() > muonPtThresh_) && (pfRelIso < 0.4) && m.passed(reco::Muon::Selector::CutBasedIdLoose)) { 
      return true; 
    }
  }
  return false;
}

bool NanoFilter::hasPhotons(edm::Event& iEvent) {
  /*
    Returns True if a high-pt photon is found in the event.
  */
  edm::Handle<edm::View<pat::Photon>> photons;
  iEvent.getByToken(photonToken_, photons);
  for (const auto &p : *photons) {
    if (p.pt() > photonPtThresh_) { return true; }
  }
  return false;
}

// ------------ method called on each new Event  ------------
bool NanoFilter::filter(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  edm::Handle<edm::View<pat::Jet>> jets;
  edm::Handle<edm::View<pat::MET>> mets;

  iEvent.getByToken(jetToken_, jets);
  iEvent.getByToken(metToken_, mets);

  // At least two jets, with a pt cut on leading jet
  if (jets->size() < nJetMinThresh_) { return false; }
  if ((*jets)[0].pt() < jetPtThresh_) { return false; }

  // Check for leptons
  if ( hasElectrons(iEvent) ) { return true; }
  if ( hasMuons(iEvent) )     { return true; }
  if ( hasPhotons(iEvent) )   { return true; }

  // If there are no leptons, check for high MET
   const pat::MET &met = mets->front();
   if (met.pt() > metPtThresh_) { return true; }

  return false;
}

// ------------ method called once each stream before processing any runs, lumis or events  ------------
void NanoFilter::beginStream(edm::StreamID) {
  // please remove this method if not needed
}

// ------------ method called once each stream after processing all runs, lumis and events  ------------
void NanoFilter::endStream() {
  // please remove this method if not needed
}

// ------------ method called when starting to processes a run  ------------
/*
void
NanoFilter::beginRun(edm::Run const&, edm::EventSetup const&)
{ 
}
*/

// ------------ method called when ending the processing of a run  ------------
/*
void
NanoFilter::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when starting to processes a luminosity block  ------------
/*
void
NanoFilter::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a luminosity block  ------------
/*
void
NanoFilter::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void NanoFilter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}
//define this as a plug-in
DEFINE_FWK_MODULE(NanoFilter);
