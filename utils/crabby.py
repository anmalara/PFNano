#! /usr/bin/env python3
import os, yaml, argparse, copy, importlib
import string, random, hashlib
from multiprocessing import Process

# use python3 because crab client needs to call LumiList with python3 script
from CRABAPI.RawCommand import crabCommand
from http.client import HTTPException  # in python3, http.client replaces httplib

from utils.colors import cyan, green, blue, red, orange, yellow


def run_crab_command(command, config):
    dir = config.General.workArea + "/crab_" + config.General.requestName
    try:
        if command == "submit":
            crabCommand(command=command, config=config)
        if command == "resubmit":
            crabCommand(command=command, dir=dir)
    except HTTPException as hte:
        print(red("Cannot execute command"))
        print(red(hte.headers))


def rnd_str(N, seedstr="test"):
    # Seed with dataset name hash to be reproducible
    random.seed(int(hashlib.sha512(seedstr.encode("utf-8")).hexdigest(), 16))
    letters = string.ascii_letters
    return "".join(random.choice(letters) for _ in range(N))


def parse_args():
    parser = argparse.ArgumentParser(description="Submit jobs")
    parser.add_argument("-c", "--card", dest="card", default="utils/config_mc.yml", help="Crab yaml card")
    parser.add_argument("-m", "--make", action="store_true", help="Make crab configs according to the spec.")
    parser.add_argument("--submit", action="store_true", help="Submit configs created by ``--make``.")
    parser.add_argument("--resubmit", action="store_true", help="Submit configs created by ``--make``.")
    parser.add_argument("--status", action="store_true", help="Run `crab submit` and print nicely.")
    parser.add_argument("--test", action="store_true", help="Test submit - only 1 file, don't publish.")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    with open(args.card, "r") as f:
        card = yaml.safe_load(f)
        card = card["campaign"]

    template_crab = "utils/template_crab.py"
    tag_extension = card["tag_extension"]
    datasets_name = card["datasets"]
    isData = card["data"]
    work_area = f"./work_area/{tag_extension}/" + os.path.basename(card["config"]).replace(
        "_NANO", ""
    ).replace(".py", "/")
    print(cyan(f"Working area: {work_area}"))
    if os.path.isdir(work_area):
        if args.submit or args.make:
            if input(yellow(f"``workArea: {work_area}`` already exists. Continue? (y/n)")) != "y":
                exit()
    os.makedirs(work_area, exist_ok=True)

    with open(template_crab, "r") as template_file:
        base_crab_config = template_file.read()

    if datasets_name.endswith(".txt"):
        with open(datasets_name, "r") as dataset_file:
            datasets = [d for d in dataset_file.read().split() if len(d) > 10 and not d.startswith("#")]
    else:
        datasets = [d for d in datasets_name.split("\n") if len(d) > 10 and not d.startswith("#")]

    for dataset in datasets:
        print(green("   ==> " + dataset))
        crab_config = copy.deepcopy(base_crab_config)
        infos = dataset.split("/")[1:2]
        ver = dataset.split("/")[2].split("-")
        if not "SIM" in dataset.split("/")[-1]:
            infos += ver[0:1]
            infos += ver[1].split("_")[1:]
        if "_ext" in dataset:
            infos += ver[1].split("_")[-1:]
        dataset_name = "_".join(infos)

        tag = f"{dataset.split('/')[2]}_{tag_extension}"

        if len(dataset_name) < 95:
            request_name = dataset_name
        else:
            request_name = dataset_name[:90] + rnd_str(8, dataset_name)

        cfg_filename = os.path.join(work_area, f"submit_{dataset_name}.py")
        cfg_dir = os.path.join(work_area, "crab_" + request_name)

        if args.make:
            if os.path.isdir(cfg_dir):
                raise RuntimeError(f"Crab dir already exists: {cfg_dir}")
            os.makedirs(cfg_dir, exist_ok=True)
            card_info = {
                "_requestName_": request_name,
                "_workArea_": work_area,
                "_psetName_": card["config"],
                "_inputDataset_": dataset,
                "_outLFNDirBase_": f"{card['outLFNDirBase']}/{tag_extension}/",
                "_storageSite_": card["storageSite"],
                "_publication_": "True",
                # "_splitting_": "FileBased",
                # "_unitsPerJob_": "1",
                "_splitting_": "EventAwareLumiBased",
                "_unitsPerJob_": "100000",
                "_outputDatasetTag_": tag,
            }
            verbatim_lines = []
            if args.test:
                verbatim_lines.append("config.Data.totalUnits = 1")
                card_info["_publication_"] = "False"
            else:
                verbatim_lines.append("config.Data.totalUnits = -1")

            if isData:
                verbatim_lines.append("config.JobType.maxJobRuntimeMin = 2750")

            for line in verbatim_lines:
                crab_config += "\n" + line
            crab_config += "\n"

            for key, info in card_info.items():
                crab_config = crab_config.replace(key, info)

            with open(cfg_filename, "w") as cfg_file:
                cfg_file.write(crab_config)

        if args.submit or args.resubmit:
            if args.submit:
                mode = "submit"
                if os.path.isdir(cfg_dir):
                    os.rmdir(cfg_dir)
            if args.resubmit:
                mode = "resubmit"
            print(green(f"{mode.capitalize()}ting configs:"))
            config_module = importlib.import_module(
                cfg_filename.replace("/", ".").replace(".py", "").lstrip("..")
            )
            p = Process(target=run_crab_command, kwargs={"command": mode, "config": config_module.config})
            p.start()
            p.join()

        if args.status:
            status_cases = [
                "unsubmitted",
                "idle",
                "finished",
                "running",
                "transferred",
                "transferring",
                "unsubmitted",
                "failed",
            ]
            o = os.popen("crab status " + cfg_dir).read().split("\n")

            for i, line in enumerate(o):
                if line.startswith("CRAB project directory:"):
                    print(blue(line))  # in python3, print(line) replaces print line
                if line.startswith("Jobs status"):
                    for j in range(5):
                        if len(o[i + j]) < 2:
                            continue
                        if any(s in o[i + j] for s in status_cases):
                            print(orange(o[i + j]))

                if "Output dataset" in line:
                    das_name = line.split()[-1]
                    if "DAS URL" in line:
                        print(green(f" --> link: {das_name}"))
                    else:
                        print(green(f" --> Published in: {das_name}"))


if __name__ == "__main__":
    main()
