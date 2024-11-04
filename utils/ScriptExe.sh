#!/bin/bash

echo "===================================================================================================="
echo "ScriptExe.sh: Step -1: Input Arguments"
echo "===================================================================================================="
echo $@


echo "===================================================================================================="
echo "ScriptExe.sh: Step 0: Dumping PSet"
echo "===================================================================================================="
python3 -c "import PSet; print(PSet.process.dumpPython())"


echo "===================================================================================================="
echo "ScriptExe.sh: Step 1: Make Skim NanoAOD"
echo "===================================================================================================="
echo "Executing: cmsRun PSet.py"
cmsRun -j FrameworkJobReport.xml -p PSet.py
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