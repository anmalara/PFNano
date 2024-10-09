#!/bin/bash

# Add some space at the beginning for better readability in the logs

echo "===================================================================================================="
echo "ScriptExe.sh: Step 1: Make Skim NanoAOD"
echo "===================================================================================================="
echo "Executing: cmsRun utils/nano_mc_2022_NANO.py"
cmsRun utils/nano_mc_2022_NANO.py
if [ $? -ne 0 ]; then
  echo "Error: cmsRun failed. Exiting."
  exit 1
fi

# Find the generated ROOT file
NTUPLE=$(ls *NanoAOD*.root | head -n 1)
NTUPLE_TEMP="ntuple.root"
HIST_TEMP="hists_nevents.root"
if [ -z "$NTUPLE" ]; then
  echo "Error: No ROOT file found. Exiting."
  exit 1
fi

echo "Moving $NTUPLE to ${NTUPLE_TEMP}"
mv ${NTUPLE} ${NTUPLE_TEMP}

# Add some space for better readability in the logs
echo -e "\n\n"
echo "===================================================================================================="
echo "ScriptExe.sh: Step 2: Merge all histograms created for different cycle numbers"
echo "===================================================================================================="
echo "Executing: python3 mergeHistogramInFile.py"
python3 mergeHistogramInFile.py
if [ $? -ne 0 ]; then
  echo "Error: Histogram merging script failed. Exiting."
  exit 1
fi

echo "Removing intermediate file histograms.root"
rm histograms.root

# Add some space for better readability in the logs
echo -e "\n\n"
echo "===================================================================================================="
echo "ScriptExe.sh: Step 3: Merge histograms and tree"
echo "===================================================================================================="
echo "Executing: hadd -f ${NTUPLE} ${HIST_TEMP} ${NTUPLE_TEMP}"
hadd -f ${NTUPLE} ${HIST_TEMP} ${NTUPLE_TEMP}
if [ $? -ne 0 ]; then
  echo "Error: hadd command failed. Exiting."
  exit 1
fi

echo "Removing intermediate file ${NTUPLE_TEMP}"
rm ${NTUPLE_TEMP} ${HIST_TEMP}

echo "Script completed successfully!"