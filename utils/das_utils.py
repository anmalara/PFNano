#!/usr/bin/env python3

import os, subprocess, yaml
from collections import OrderedDict
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


def create_card(driver_name, datasets, data):
    os.makedirs("utils/cards", exist_ok=True)
    card_name = datasets.replace("datasets/", "utils/cards/card_").replace(".txt", ".yml")
    print(blue(f"Creating card: {card_name}"))

    config = f"utils/nano_{driver_name}_NANO.py"
    if not os.path.exists(config):
        raise ValueError(red(f"Config not found :{config}. Please run ./utils/create_drivers.py"))

    card_info = {
        "campaign": {
            "storageSite": "T2_CH_CERN",
            "outLFNDirBase": "/store/group/phys_higgs/vbfhiggs",
            "tag_extension": "NanoV12",
            "config": config,
            "data": data,
            "datasets": datasets,
        }
    }

    with open(card_name, "w") as yaml_file:
        yaml.dump(card_info, yaml_file, default_flow_style=False)


def run_data():
    jetmet = ["JetHT", "MET", "JetMET", "JetMET0", "JetMET1"]
    egamma = ["EGamma", "EGamma0", "EGamma1"]
    muon = ["Muon", "Muon0", "Muon1"]
    datasets = jetmet + egamma + muon
    tag = "22Sep2023"
    year_run_map = {
        "2022_CD": {"tag": tag, "driver": f"data_2022_CDE", "year": "2022", "runs": ["C", "D"]},
        "2022_E": {"tag": tag, "driver": f"data_2022_CDE", "year": "2022", "runs": ["E"]},
        "2022_FG": {"tag": tag, "driver": f"data_2022_FG", "year": "2022", "runs": ["F", "G"]},
        "2023_CD": {"tag": f"{tag}_v*", "driver": f"data_2023_CD", "year": "2023", "runs": ["C", "D"]},
    }

    for name, info in year_run_map.items():
        tag = info["tag"]
        driver_name = info["driver"]
        year = info["year"]
        runs = info["runs"]
        tags = [f"Run{year}{run}-{tag}" for run in runs]
        fname = f"datasets/data_{name}.txt"
        create_das_dataset_list(datasets=datasets, tags=tags, fname=fname, aod="MINIAOD")
        create_card(driver_name=driver_name, datasets=fname, data=True)


def run_mc():
    year_campaign_map = {
        "2022": {"campaign": "22", "driver": f"mc_2022"},
        "2022_EE": {"campaign": "22EE", "driver": f"mc_2022_EE"},
    }

    tune_energy = "TuneCP5_13p6TeV"
    njets = ["1J", "2J"]
    pts_vjet = ["40to100", "100to200", "200to400", "400to600", "600"]

    datasets_map = {
        # Signal
        "HToInvisible": [f"{higgs}_M-125_{tune_energy}_powheg-pythia8" for higgs in ["VBFHToInvisible"]],
        # V+jet
        "QCD_Zjet": [
            f"DYto2L-2Jets_MLL-50_PTLL-{pt}_{nJ}_{tune_energy}_amcatnloFXFX-pythia8"
            for nJ in njets
            for pt in pts_vjet
        ],
        "QCD_Wjet": [
            f"WtoLNu-2Jets_PTLNu-{pt}_{nJ}_{tune_energy}_amcatnloFXFX-pythia8"
            for nJ in njets
            for pt in pts_vjet
        ],
        "EWK_Vjet": [
            f"{v}_{tune_energy}_madgraph-pythia8" for v in ["VBFto2L_MLL-50", "VBFto2Nu", "VBFtoLNu"]
        ],
        # gamma+jet
        "QCD_gjet": [
            f"G-4Jets_HT-{pt}_{tune_energy}_madgraphMLM-pythia8"
            for pt in ["40to70", "70to100", "100to200", "200to400", "400to600", "600"]
        ],
        "EWK_gjet": [f"VBFtoG_PTG-{pt}_{tune_energy}_madgraph-pythia8" for pt in ["100to200", "200"]],
        # Minor backgrounds
        "Diboson": [f"{vv}_{tune_energy}_pythia8" for vv in ["WZ", "WW", "ZZ"]],
        "ttbar": [f"{tt}_{tune_energy}_powheg-pythia8" for tt in ["TTto2L2Nu", "TTto4Q", "TTtoLNu2Q"]],
    }

    for year, info in year_campaign_map.items():
        campaign = info["campaign"]
        driver_name = info["driver"]
        tags = [f"Run3Summer{campaign}MiniAODv4"]
        for name, datasets in datasets_map.items():
            fname = f"datasets/mc_{year}_{name}.txt"
            create_das_dataset_list(datasets=datasets, tags=tags, fname=fname, aod="MINIAODSIM")
            create_card(driver_name=driver_name, datasets=fname, data=False)


def main():
    run_data()
    run_mc()
    return


if __name__ == "__main__":
    main()
