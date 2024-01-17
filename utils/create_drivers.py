#!/usr/bin/env python

import os
from utils.colors import green, blue


def create_driver(name, info):
    GT = info["GT"]
    type = info["type"]
    driver_name = f"nano_{type}_{name}"
    eventcontent = "NANOAOD" if type == "data" else "NANOAODSIM"
    custom_type = "Data" if type == "data" else "MC"
    customs = [
        f"PhysicsTools/PFNano/puppiJetMETReclustering_cff.nanoPuppiReclusterCustomize_{custom_type}",
        f"PhysicsTools/PFNano/pfnano_cff.PFnano_customize{custom_type}",
    ]
    command = f"cmsDriver.py {driver_name} --{type} --eventcontent {eventcontent} --datatier {eventcontent} --step NANO --conditions {GT} --era Run3 --nThreads 4 -n -1 --no_exec"
    for custom in customs:
        command += f" --customise={custom}"
    command += f" --customise_commands=\"process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)));process.MessageLogger.cerr.FwkReport.reportEvery=1000;process.{eventcontent}output.fakeNameForCrab = cms.untracked.bool(True)\""
    print(blue("Creating driver with:"))
    print(green("  --> " + command))
    os.system(command)
    print(blue("Moved to ./utils/"))
    os.system(f"mv {driver_name}_NANO.py utils/")


def run_data():
    datasets = ["JetHT", "MET", "JetMET", "JetMET0", "JetMET1", "EGamma", "EGamma0", "EGamma1", "Muon", "Muon0", "Muon1"]
    year_run_map = {
        "2022_CDE": {"GT": "130X_dataRun3_v2", "type": "data"},
        "2022_FG": {"GT": "130X_dataRun3_PromptAnalysis_v1", "type": "data"},
        "2023_CD": {"GT": "130X_dataRun3_PromptAnalysis_v1", "type": "data"},
        "Run3": {"GT": "130X_mcRun3_2022_realistic_v5", "type": "mc"},
        "Run3_EE": {"GT": "130X_mcRun3_2022_realistic_postEE_v6", "type": "mc"},
    }
    for name, info in year_run_map.items():
        create_driver(name=name, info=info)


def main():
    run_data()
    # run_mc()
    return


if __name__ == "__main__":
    main()
