# Biomarkers Project: Gait Analysis Pipeline

This script (`biomarkers_gait_analysis.py`) performs automated gait metric extraction, video cropping, and OpenSim visualization for OpenCap session data.

## Features
- Extracts scalar spatiotemporal metrics for both left and right gait cycles:
  - Gait speed
  - Stride length
  - Step width
  - Cadence
  - Double support time
  - Step length symmetry
- Crops synchronized videos (Cam0 and Cam1) to one representative gait cycle per side
- Saves results as:
  - Per-session CSV (`gait_metrics_pass1.csv`)
  - Appends to a master CSV (`gait_metrics_compiled.csv`) after confirmation
- Launches OpenSim GUI and opens the trial model file for visual verification
- Auto-opens folder with cropped videos
- Logs duplicates and session outcomes to a log file

## How To Use
1. Edit the sessionDir path in the __main__ section of the script to point to a session:
```
sessionDir = r"C:\path\to\OpenCapData_<session_id>"
```

2. Run the script: 
```
python biomarkers_gait_analysis.py
```

3. After review in OpenSim, confirm whether to include in the compiled spreadsheet.

## Output
Gait_Analysis_Pass1/gait_metrics_pass1.csv — per-session results

gait_metrics_compiled.csv — cumulative master sheet

gait_metrics_log.txt — timestamped log of sessions

Cropped videos saved under:
Videos/Cam0/InputMedia/<trial>/trial_sync_cropped_<r/l>_cycleX.mp4

## Notes
If multiple trials contain “walk” in their name, it will throw an error to prevent ambiguity.
Duplicate sessions in the master CSV are detected and skipped automatically.



