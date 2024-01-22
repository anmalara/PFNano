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
cd $CMSSW_BASE/src
scram b -j 10
cd PhysicsTools/PFNano

cp $CMSSW_BASE/src/PhysicsTools/PFNano/utils/NanoFilter/plugins/BuildFile.xml $CMSSW_BASE/src/PhysicsTools/NanoFilter/plugins/BuildFile.xml 
cp $CMSSW_BASE/src/PhysicsTools/PFNano/utils/NanoFilter/plugins/NanoFilter.cc $CMSSW_BASE/src/PhysicsTools/NanoFilter/plugins/NanoFilter.cc

source setup.sh
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



## Submission to CRAB

For crab submission a handler script `utils/crabby.py`, a crab baseline template `utils/template_crab.py` are provided. Yaml files are also provided: one per `data/mc` and `year`: `config_{type}_{year}.yml`.

`crabby.py` has the following options:
- make:
  ```
  python3 utils/crabby.py -c utils/config_{type}_{year}.yml --make
  ```
- submit
  ```
  python3 utils/crabby.py -c utils/config_{type}_{year}.yml --submit
  ```
- resubmit
  ```
  python3 utils/crabby.py -c utils/config_{type}_{year}.yml --resubmit
  ```
- other options are not tested/supported yet.
