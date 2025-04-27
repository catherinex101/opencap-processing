# OpenCap Gait Analysis for SubLSS

This script computes scalar gait metrics and gait cycle-averaged kinematic curves from OpenCap data.

Adapted from the OpenCap example `example_gait_analysis.py`.  
Modified by Catherine for the SNAPL SubLSS study.

## Setup

Make sure you have OpenCap-processing installed and your Anaconda environment ready.

## How to Run

1. Open **Anaconda Powershell Prompt**.
2. Activate environment: conda activate opencap
3. Navigate to the script directory: cd "C:\Users\cxiang\Documents\GitHub\opencap-processing\subLSS"
4. Run the analysis script: python sublss_gait_analysis.py


Before running:
- Modify `sessionDir` and `trialName` variables inside the script if necessary.
- Add your OpenCap data files into `Data\sub-LSSPilot\` folder.

## Outputs

- Right and left foot gait metrics will print directly in the Anaconda Prompt.
- Kinematics graphs will pop up for review.
- After closing the graph, a gait analysis table will be exported to your specified output directory.

## License

Licensed under the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0).

---
