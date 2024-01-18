source /cvmfs/cms.cern.ch/crab3/crab.sh
voms-proxy-init -rfc -voms cms -valid 192:00

cmsenv

export PFNANO_PATH=$(pwd -L)
export PYTHONPATH=${PFNANO_PATH}:${PYTHONPATH}
