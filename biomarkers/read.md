# Biomarkers Project: Gait Analysis Pipeline

This script (`biomarkers_gait_analysis.py`) performs automated gait metric extraction, video cropping, and OpenSim visualization for OpenCap session data.

## Summary
This script processes one OpenCap session folder at a time. It:
- Extracts gait metrics (e.g., speed, cadence, symmetry)
- Crops video clips for left/right gait cycles
- Saves metrics to a per-session CSV
- Opens the CSV and OpenSim GUI for manual review
- Prompts you to decide whether to include the metrics in a compiled spreadsheet
- Logs your decision and prevents duplicates

## How To Use
1. Edit the sessionDir path in the __main__ section of the script to point to a session:
```
sessionDir = r"C:\path\to\OpenCapData_<session_id>"
```

1.5. Adjust the buffer if necessary. 

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

Recommend that you first batch download the Opencap data into local folder using `batchDownload.py`. Any duplicate folders will be skipped, as to not overwrite existing data stored locally in the folders and not tracked on version control (Github) due to the sensitive information.



