#!/usr/bin/env python

import os, subprocess
from utils.colors import cyan, green, blue, red


def dasgoclient(commands, fname, overwrite=False, extend=True, remove=False):
    if overwrite == extend:
        raise ValueError(red("Combination not allowed"))

    test_name = "test.txt"
    with open(test_name, "w") as f:
        for command in commands:
            subprocess.call(command, shell=True, stdout=f)

    samples = []
    if os.path.exists(fname) and extend:
        with open(fname, "r") as f:
            for l in f.readlines():
                l = l.strip()
                samples.append(l)

    print(blue(f"Starting with {len(samples)} samples:"))
    print(cyan(f"    -->: {samples}"))

    with open(test_name, "r") as f:
        for l in f.readlines():
            sample = l.strip()
            if not overwrite and sample in samples:
                continue
            samples.append(sample)

    print(blue(f"Storing {len(samples)} samples:"))
    print(green(f"    -->: {samples}"))

    if len(samples) != len(list(set(samples))):
        raise RuntimeError(red("Unexpected number of files: duplicates are found"))

    with open(fname, "w") as f:
        for sample in samples:
            f.write(f"{sample}\n")

    subprocess.call(["rm", test_name])
    if remove:
        subprocess.call(["rm", fname])
    return samples


def create_das_dataset_list(datasets, tags, fname, aod):
    commands = []
    for dataset in datasets:
        for tag in tags:
            cmd = f'dasgoclient -query="dataset=/{dataset}/*{tag}-*/{aod} dataset status= VALID"'
            commands.append(cmd)

    dasgoclient(commands=commands, fname=fname)


def run_data():
    datasets = ["JetHT", "MET", "JetMET", "JetMET0", "JetMET1", "EGamma", "EGamma0", "EGamma1", "Muon", "Muon0", "Muon1"]
    year_run_map = {
        "2022_CD": {"tag": "22Sep2023", "year": "2022", "runs": ["C", "D"]},
        "2022_E": {"tag": "22Sep2023", "year": "2022", "runs": ["E"]},
        "2022_FG": {"tag": "22Sep2023", "year": "2022", "runs": ["F", "G"]},
        "2023_CD": {"tag": "22Sep2023_v*", "year": "2023", "runs": ["C", "D"]},
    }

    for name, info in year_run_map.items():
        tag = info["tag"]
        year = info["year"]
        runs = info["runs"]
        tags = [f"Run{year}{run}-{tag}" for run in runs]
        fname = f"datasets/data_{name}.txt"
        create_das_dataset_list(datasets=datasets, tags=tags, fname=fname, aod="MINIAOD")


def run_mc():
    year_campaign_map = {
        "2022": {"campaign": "22"},
        "2022EE": {"campaign": "22EE"},
    }

    datasets = []

    # HToInvisible
    datasets += [f"{higgs}_M-125_TuneCP5_13p6TeV_powheg-pythia8" for higgs in ["VBFHToInvisible"]]
    # EWK V+jet
    datasets += [f"{v}_TuneCP5_13p6TeV_madgraph-pythia8" for v in ["VBFto2L_MLL-50", "VBFto2Nu", "VBFtoLNu"]]
    # Diboson
    datasets += [f"{vv}_TuneCP5_13p6TeV_pythia8" for vv in ["WZ", "WW", "ZZ"]]
    # ttbar
    datasets += [f"{tt}_TuneCP5_13p6TeV_powheg-pythia8" for tt in ["TTto2L2Nu", "TTto4Q", "TTtoLNu2Q"]]
    # QCD gamma+jet
    datasets += [f"G-4Jets_HT-{pt}_TuneCP5_13p6TeV_madgraphMLM-pythia8" for pt in ["40to70", "70to100", "100to200", "200to400", "400to600", "600"]]
    # EWK gamma+jet
    datasets += [f"VBFtoG_PTG-{pt}_TuneCP5_13p6TeV_madgraph-pythia8" for pt in ["100to200", "200"]]

    for year, info in year_campaign_map.items():
        campaign = info["campaign"]
        tags = [f"Run3Summer{campaign}MiniAODv4"]
        fname = f"datasets/mc_{year}.txt"
        create_das_dataset_list(datasets=datasets, tags=tags, fname=fname, aod="MINIAODSIM")


def main():
    run_data()
    run_mc()
    return


if __name__ == "__main__":
    main()
