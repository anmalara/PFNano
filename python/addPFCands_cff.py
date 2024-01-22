import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import Var, CandVars


def addPFCands(process, runOnMC=False):
    cut = "     ( (fromPV()   <=  3 ) || ( pt > 0.1  ) )"
    cut += " && ( (fromPV()   >=  2 ) || ( pt > 3    ) )"
    cut += " && ( (abs(pdgId) != 22 ) || ( pt > 0.8  ) )"  # pt cut on photons
    cut += " && ( (abs(pdgId) != 130) || ( pt > 2.0  ) )"  # pt cut on neutral hadrons
    cut += " && ( (abs(pdgId) != 1  ) || ( pt > 2.5  ) )"  # pt cut on HF hadronic
    cut += " && ( (abs(pdgId) != 2  ) || ( pt > 2.5  ) )"  # pt cut on HF EM
    cut += " && ( (abs(pdgId) != 211) || ( pt*puppiWeight > 0.01 ) )"  # pt cut on charged hadron

    process.customizedPFCandsTask = cms.Task()
    process.schedule.associate(process.customizedPFCandsTask)
    process.customConstituentsExtTable = cms.EDProducer(
        "SimpleCandidateFlatTableProducer",
        src=cms.InputTag("packedPFCandidates"),
        cut=cms.string(cut),
        name=cms.string("PFCands"),
        doc=cms.string("ParticleFlow candidates"),
        singleton=cms.bool(False),  # the number of entries is variable
        extension=cms.bool(False),  # this is the extension table for the AK8 constituents
        maxLen=cms.uint32(500),
        variables=cms.PSet(
            CandVars,
            puppiWeight=Var("puppiWeight()", float, doc="Puppi weight", precision=10),
            puppiWeightNoLep=Var("puppiWeightNoLep()", float, doc="puppiWeightNoLep", precision=10),
            vtxChi2=Var("?hasTrackDetails()?vertexChi2():-1", float, doc="vertex chi2", precision=10),
            trkChi2=Var(
                "?hasTrackDetails()?pseudoTrack().normalizedChi2():-1",
                float,
                doc="normalized trk chi2",
                precision=10,
            ),
            dz=Var("?hasTrackDetails()?dz():-1", float, doc="pf dz", precision=10),
            dzErr=Var("?hasTrackDetails()?dzError():-1", float, doc="pf dz err", precision=10),
            d0=Var("?hasTrackDetails()?dxy():-1", float, doc="pf d0", precision=10),
            d0Err=Var("?hasTrackDetails()?dxyError():-1", float, doc="pf d0 err", precision=10),
            pvAssocQuality=Var(
                "pvAssociationQuality()",
                int,
                doc="primary vertex association quality. 0: NotReconstructedPrimary, 1: OtherDeltaZ, 4: CompatibilityBTag, 5: CompatibilityDz, 6: UsedInFitLoose, 7: UsedInFitTight",
            ),
            lostInnerHits=Var(
                "lostInnerHits()",
                int,
                doc="lost inner hits. -1: validHitInFirstPixelBarrelLayer, 0: noLostInnerHits, 1: oneLostInnerHit, 2: moreLostInnerHits",
            ),
            lostOuterHits=Var(
                "?hasTrackDetails()?pseudoTrack().hitPattern().numberOfLostHits('MISSING_OUTER_HITS'):0",
                int,
                doc="lost outer hits",
            ),
            numberOfHits=Var("numberOfHits()", int, doc="number of hits"),
            numberOfPixelHits=Var("numberOfPixelHits()", int, doc="number of pixel hits"),
            trkQuality=Var("?hasTrackDetails()?pseudoTrack().qualityMask():0", int, doc="track quality mask"),
            trkHighPurity=Var(
                "?hasTrackDetails()?pseudoTrack().quality('highPurity'):0", bool, doc="track is high purity"
            ),
            trkAlgo=Var("?hasTrackDetails()?pseudoTrack().algo():-1", int, doc="track algorithm"),
            trkP=Var("?hasTrackDetails()?pseudoTrack().p():-1", float, doc="track momemtum", precision=-1),
            trkPt=Var("?hasTrackDetails()?pseudoTrack().pt():-1", float, doc="track pt", precision=-1),
            trkEta=Var("?hasTrackDetails()?pseudoTrack().eta():-1", float, doc="track pt", precision=12),
            trkPhi=Var("?hasTrackDetails()?pseudoTrack().phi():-1", float, doc="track phi", precision=12),
            energy=Var("energy()", "float", precision=10, doc="PF candidate energy"),
            Vtx_x=Var("vertex().x()", "float", precision=10, doc="vertex x pos"),
            Vtx_y=Var("vertex().y()", "float", precision=10, doc="vertex y pos"),
            Vtx_z=Var("vertex().z()", "float", precision=10, doc="vertex z pos"),
            caloFrac=Var("caloFraction()", "float", precision=10, doc="CALO energy fraction"),
            hcalFrac=Var("hcalFraction()", "float", precision=10, doc="HCAL energy fraction"),
            dzAssociatedPV=Var("dzAssociatedPV()", "float", precision=10, doc="dz with respect to the PV"),
            isIsoChHad=Var("isIsolatedChargedHadron()", "int", doc="Is isolated charged hadron?"),
            fromPV=Var("fromPV()", "int", doc="Is associated to the PV?"),
        ),
    )

    process.customizedPFCandsTask.add(process.customConstituentsExtTable)

    if runOnMC:
        process.genJetsParticleTable = cms.EDProducer(
            "SimpleCandidateFlatTableProducer",
            src=cms.InputTag("packedGenParticles"),
            cut=cms.string(""),  # we should not filter after pruning
            name=cms.string("GenCands"),
            doc=cms.string("interesting gen particles from AK4 and AK8 jets"),
            singleton=cms.bool(False),  # the number of entries is variable
            extension=cms.bool(False),  # this is the main table for the AK8 constituents
            variables=cms.PSet(CandVars),
            maxLen=cms.uint32(500),
        )
        process.customizedPFCandsTask.add(process.genJetsParticleTable)

    process = addEventFilter(process, runOnMC=runOnMC)
    return process


def addEventFilter(process, runOnMC):
    process.nanoFilter = cms.EDFilter(
        "NanoFilter",
        jets=cms.InputTag("linkedObjects", "jets"),
        met=cms.InputTag("slimmedMETs"),
        electrons=cms.InputTag("linkedObjects", "electrons"),
        muons=cms.InputTag("linkedObjects", "muons"),
        photons=cms.InputTag("linkedObjects", "photons"),
        metPtMin=cms.double(100.0),
        nJetMin=cms.uint32(2),
        jetPtMin=cms.double(20.0),
        electronPtMin=cms.double(20.0),
        muonPtMin=cms.double(20.0),
        photonPtMin=cms.double(150.0),
    )

    if runOnMC:
        process.nanoSequenceMC.insert(
            process.nanoSequenceMC.index(process.nanoSequenceCommon) + 1, process.nanoFilter
        )
    else:
        process.nanoSequence.insert(
            process.nanoSequence.index(process.nanoSequenceCommon) + 1, process.nanoFilter
        )

    return process
