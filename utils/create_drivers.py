#!/usr/bin/env python3

import os
from utils.colors import green, blue


def modify_file(file_path):

    with open(file_path, "r") as file:
        lines = file.readlines()

    modified_lines = []

    # Loop through each line and add modifications when the match is found
    for line in lines:
        modified_lines.append(line)

        if "outputCommands=process.NANOAOD" in line and "EventContent.outputCommands," in line:
            modified_lines.append(
                '    SelectEvents=cms.untracked.PSet(SelectEvents=cms.vstring("nanoAOD_step")),\n'
            )

        if "Additional output definition" in line:
            modified_lines.append(
                'process.TFileService = cms.Service("TFileService", fileName=cms.string("histograms.root"))\n'
            )

    with open(file_path, "w") as file:
        file.writelines(modified_lines)

    print(f"File '{file_path}' successfully modified.")


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
    os.system(f"black utils/{driver_name}_NANO.py")
    modify_file(f"utils/{driver_name}_NANO.py")


def main():
    year_run_map = {
        "2022_CDE": {"GT": "130X_dataRun3_v2", "type": "data"},
        "2022_FG": {"GT": "130X_dataRun3_PromptAnalysis_v1", "type": "data"},
        "2023_CD": {"GT": "130X_dataRun3_PromptAnalysis_v1", "type": "data"},
        "2022": {"GT": "130X_mcRun3_2022_realistic_v5", "type": "mc"},
        "2022_EE": {"GT": "130X_mcRun3_2022_realistic_postEE_v6", "type": "mc"},
        "2023": {"GT": "130X_mcRun3_2023_realistic_v14", "type": "mc"},
        "2023_BPix": {"GT": "130X_mcRun3_2023_realistic_postBPix_v2", "type": "mc"},
    }

    for name, info in year_run_map.items():
        create_driver(name=name, info=info)

    return


if __name__ == "__main__":
    main()
