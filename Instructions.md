# Instructions for Hinv samples

More general info can be found in the ReadME file.
This information overrules the instuctions in the ReadME file.

## Recipe

At the moment, job submission to CRAB is possible only from `lxplus8`. Make sure you compile from the correct environment. Ask if you need help!!!

```
cmsrel CMSSW_13_0_13
cd CMSSW_13_0_13/src
cmsenv
git cms-merge-topic colizz:dev-130X-addNegPNet
git clone https://github.com/cms-jet/PFNano.git PhysicsTools/PFNano -b 13_0_7_from124MiniAOD
cd PhysicsTools
mkedfltr NanoFilter
cd PFNano
git remote add anmalara git@github.com:anmalara/PFNano.git
git pull anmalara 13_0_13

cp $CMSSW_BASE/src/PhysicsTools/PFNano/utils/NanoFilter/plugins/BuildFile.xml $CMSSW_BASE/src/PhysicsTools/NanoFilter/plugins/BuildFile.xml 
cp $CMSSW_BASE/src/PhysicsTools/PFNano/utils/NanoFilter/plugins/NanoFilter.cc $CMSSW_BASE/src/PhysicsTools/NanoFilter/plugins/NanoFilter.cc

cd $CMSSW_BASE/src
scram b -j 10
cd PhysicsTools/PFNano

source setup.sh

python3 -m pip install black
```

Remeber to source the `setup.sh` file at each login.
```
source setup.sh
```

## Local Usage:

There are python config files ready to run in `PhysicsTools/PFNano/utils/`.

To create the list of samples to run on, modify as it fits and then run:
```
./utils/create_cards.py
```

To create the driver to produce nano files, modify as it fits and then run:
```
./utils/create_drivers.py
```

N.b.
If you want to apply filters, remember to apply this line to `cms.OutputModule`.
```
SelectEvents=cms.untracked.PSet(SelectEvents=cms.vstring("nanoAOD_step")),
```

Remember to also define an EDFilter.
Currently this is done within the setup/installation.
Since this filter stores histograms, you **MUST** include this line:
```
process.TFileService = cms.Service("TFileService", fileName=cms.string("histograms.root"))
```
This changes are currenlty implemented wihtin `utils/create_drivers.py`.



## Submission to CRAB

For crab submission a handler script `utils/crabby.py`, a crab baseline template `utils/template_crab.py` are provided. 
Yaml files are also provided: one per `data/mc`, `year` and sample: `card_{type}_{year}_{sample}.yml`.

The crab baseline template `utils/template_crab.py` contains the following line:

```bash
config.JobType.scriptExe = "utils/ScriptExe.sh"
config.JobType.inputFiles = ["utils/mergeHistogramInFile.py"]
```

This allows to run the self-created script rather than the simple `cmsRun` command. For more details, have a look at the scripts.


`crabby.py` has the following options:
- make:
  ```
  python3 utils/crabby.py -c utils/cards/card_{type}_{year}_{sample}.yml --make
  ```
- submit
  ```
  python3 utils/crabby.py -c utils/cards/card_{type}_{year}_{sample}.yml --submit
  ```
- status
  ```
  python3 utils/crabby.py -c utils/cards/card_{type}_{year}_{sample}.yml --status
  ```
- resubmit
  ```
  python3 utils/crabby.py -c utils/cards/card_{type}_{year}_{sample}.yml --resubmit
  ```
- other options are not tested/supported yet.
