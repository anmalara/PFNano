# Instructions for Hinv samples

To be read on top of the ReadME.
This overrule the previous instructions.

## Recipe


```
cmsrel CMSSW_13_0_13
cd CMSSW_13_0_13/src
cmsenv
git cms-merge-topic colizz:dev-130X-addNegPNet # adding negative tag
git clone https://github.com/cms-jet/PFNano.git PhysicsTools/PFNano -b 13_0_7_from124MiniAOD
git remote add anmalara git@github.com:anmalara/PFNano.git
git pull anmalara 13_0_13
scram b -j 10
cd PhysicsTools/PFNano
source setup.sh
```

## Local Usage:

There are python config files ready to run in `PhysicsTools/PFNano/utils/`.

To create the list of samples to run on, modify as it fits and then run:
```
./utils/das_utils.py
```

To create the driver to produce nano files, modify as it fits and then run:
```
./utils/create_drivers.py
```


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


## Processing data

No lumi mask is supported.
