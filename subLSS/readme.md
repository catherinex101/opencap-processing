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
- Modify `sessionDir` and `trialName` and `buffer` variables inside the script if necessary.
- Add your OpenCap data files into `Data\sub-LSSPilot\` folder.

## Cycle Selection Logic

To ensure accurate video-based analysis, the script only selects gait cycles that **fully occur within the camera view**. It checks the timestamp of the end of each gait cycle (`heel strike 2`) and ensures that it finishes at least a `buffer` number of seconds before the end of the video. This prevents analysis of steps where the participant may be partially or fully out of frame. The script selects the **most recent valid gait cycle** for each foot (right and left) independently and only includes them in the analysis and cropping if they meet the visibility criteria.

## Metric Averaging

In the summary table, scalar gait metrics (e.g., gait speed, step width) are **averaged across valid right and left cycles**, if both are available. The only exception is `step_length_symmetry`, which is computed solely using the **right gait cycle**.

## Outputs

- Right and left gait metrics (e.g. speed, cadence, stride length) printed to terminal.
- Kinematic time-normalized curves shown in a pop-up matplotlib graph.
- After closing the graph, a summary table of spatiotemporal gait metrics saved as gait_summary_table.csv inside a session-specific output folder.
  Cropped videos saved per camera, named with the used gait cycle index.

## License

Licensed under the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0).

---
