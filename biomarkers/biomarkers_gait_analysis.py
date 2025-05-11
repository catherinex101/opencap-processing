r'''
    ---------------------------------------------------------------------------
    OpenCap processing: biomarkers_gait_analysis.py
    ---------------------------------------------------------------------------
    Copyright 2023 Stanford University and the Authors

    Author(s): Scott Uhlrich
    Modified by Catherine
    Adapted from example: example_gait_analysis.py

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Please contact us for any questions: https://www.opencap.ai/#contact
'''

import os
import sys
import yaml
import pandas as pd
import subprocess
import cv2

sys.path.append("../")
sys.path.append("../ActivityAnalyses")

from gait_analysis import gait_analysis
from utilsPlotting import plot_dataframe_with_shading

# %% Functions.
def crop_video_ffmpeg(input_path, output_path, start_time, end_time):
    duration = end_time - start_time
    cmd = [
        'ffmpeg', '-y', '-ss', str(start_time), '-i', input_path,
        '-t', str(duration), '-an',
        '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-movflags', '+faststart', output_path
    ]
    print(f"Running ffmpeg crop: {cmd}")
    subprocess.run(cmd, check=True)
    print(f"✅ Cropped video saved to {output_path}")

def get_video_duration(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Failed to open video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frame_count / fps
    cap.release()

    print(f"\n📹 Video duration: {duration:.2f} seconds")
    return duration

def __select_valid_gait_cycle(gait_obj, video_duration_sec, buffer):
    times = gait_obj.gaitEvents['ipsilateralTime']
    # Reverse order so 0 is latest
    for i in (range(len(times))):
        _, _, hs2 = times[i]
        if hs2 + buffer <= video_duration_sec:
            print(f"✅ Selected gait cycle index: {i} (HS2 = {hs2:.2f}s)")
            return i
    raise ValueError("❌ No valid gait cycle found before video end.")

def select_valid_gait_cycle(gait_obj, video_duration_sec, buffer=0.01):
    """
    Select the latest valid gait cycle (index 0) that ends before (video_duration - buffer).
    Returns: (HS1_time, HS2_time, selected_cycle_index)
    Assumes gaitEvents['ipsilateralTime'] is ordered with latest cycle at index 0.
    """
    times = gait_obj.gaitEvents['ipsilateralTime']
    
    for i in range(len(times)):  # 0 = latest
        hs1, _, hs2 = times[i]
        if hs2 + buffer <= video_duration_sec:
            print(f"✅ Selected gait cycle index: {i} (HS2 = {hs2:.2f}s)")
            return hs1, hs2, i

    raise ValueError("❌ No valid gait cycle found before video end.")


# %% Paths.
baseDir = os.path.join(os.getcwd(), '..')
dataFolder = os.path.join(baseDir, 'Data')

scalar_names = {'gait_speed','stride_length','step_width','cadence',
                'single_support_time','double_support_time','step_length_symmetry'}

n_gait_cycles = 2
filter_frequency = 6

# Set local session path and trial name manually
sessionDir = r"C:\Users\cxiang\Documents\GitHub\opencap-processing\Data\biomarkers\OpenCapData_82b42488-8582-4801-a366-3c476719a167"
trialName = "walk"

metadata_path = os.path.join(sessionDir, 'sessionMetadata.yaml')
with open(metadata_path, 'r') as f:
    metadata = yaml.safe_load(f)

height_m = metadata['height_m']
mass_kg = metadata['mass_kg']

video_filename = f"{trialName}_sync.mp4"
cam1_path = os.path.join(sessionDir, "Videos", "Cam1", "InputMedia", trialName, video_filename)
cam0_path = os.path.join(sessionDir, "Videos", "Cam0", "InputMedia", trialName, video_filename)

video_duration_sec = min(get_video_duration(cam1_path), get_video_duration(cam0_path))

# ========== Right Gait Analysis ==========
gait_r = gait_analysis(
    sessionDir, trialName, leg='r',
    lowpass_cutoff_frequency_for_coordinate_values=filter_frequency,
    n_gait_cycles=n_gait_cycles, gait_style='overground')

gait_r.print_gait_cycle_times()

hs1_r, hs2_r, idx_r = select_valid_gait_cycle(gait_r, video_duration_sec, buffer=0.3)

# Right gait cropping and analysis
save_cam1_path_r = os.path.join(sessionDir, "Videos", "Cam1", "InputMedia", trialName, f"{trialName}_sync_cropped_r_cycle{idx_r}.mp4")
save_cam0_path_r = os.path.join(sessionDir, "Videos", "Cam0", "InputMedia", trialName, f"{trialName}_sync_cropped_r_cycle{idx_r}.mp4")

crop_video_ffmpeg(cam1_path, save_cam1_path_r, hs1_r, hs2_r)
crop_video_ffmpeg(cam0_path, save_cam0_path_r, hs1_r, hs2_r)

gaitResults = {}
gaitResults['scalars_r'] = gait_r.compute_scalars(scalar_names, selected_cycle_index=idx_r)
gaitResults['curves_r'] = gait_r.get_coordinates_normalized_time(selected_cycle_index=idx_r)

# ========== Left Gait Analysis ==========
gait_l = gait_analysis(
    sessionDir, trialName, leg='l',
    lowpass_cutoff_frequency_for_coordinate_values=filter_frequency,
    n_gait_cycles=n_gait_cycles, gait_style='overground')

gait_l.print_gait_cycle_times()

hs1_l, hs2_l, idx_l = select_valid_gait_cycle(gait_l, video_duration_sec, buffer=0.3)

# Left gait cropping and analysis
save_cam1_path_l = os.path.join(sessionDir, "Videos", "Cam1", "InputMedia", trialName, f"{trialName}_sync_cropped_l_cycle{idx_l}.mp4")
save_cam0_path_l = os.path.join(sessionDir, "Videos", "Cam0", "InputMedia", trialName, f"{trialName}_sync_cropped_l_cycle{idx_l}.mp4")

crop_video_ffmpeg(cam1_path, save_cam1_path_l, hs1_l, hs2_l)
crop_video_ffmpeg(cam0_path, save_cam0_path_l, hs1_l, hs2_l)

gaitResults['scalars_l'] = gait_l.compute_scalars(scalar_names, selected_cycle_index=idx_l)
gaitResults['curves_l'] = gait_l.get_coordinates_normalized_time(selected_cycle_index=idx_l)

# ========== Print Gait Selection ==========
print(f"🦶 Selected right gait cycle index: {idx_r}")
print(f"🦶 Selected left gait cycle index: {idx_l}")

# ========== Print Gait Analysis ==========
print('\nRight foot gait metrics:')
print('-----------------')
for key, value in gaitResults['scalars_r'].items():
    rounded_value = round(value['value'], 2)
    print(f"{key}: {rounded_value} {value['units']}")

print('\nLeft foot gait metrics:')
print('-----------------')
for key, value in gaitResults['scalars_l'].items():
    rounded_value = round(value['value'], 2)
    print(f"{key}: {rounded_value} {value['units']}")

# ========== Output Kinematics ==========
plot_dataframe_with_shading(
    [gaitResults['curves_r']['mean'], gaitResults['curves_l']['mean']],
    [gaitResults['curves_r']['sd'], gaitResults['curves_l']['sd']],
    leg = ['r','l'],
    xlabel = '% gait cycle',
    title = 'kinematics (m or deg)',
    legend_entries = ['right','left'])

avg_metrics = {}
for key in scalar_names:
    if key == 'step_length_symmetry':
        avg_metrics[key] = gaitResults['scalars_r'].get(key, {'value': None, 'units': ''})
        continue
    val_r = gaitResults['scalars_r'].get(key, {}).get('value')
    val_l = gaitResults['scalars_l'].get(key, {}).get('value')
    if val_r is not None and val_l is not None:
        unit = gaitResults['scalars_r'][key]['units']
        avg_metrics[key] = {'value': (val_r + val_l) / 2, 'units': unit}

# ========== Output Gait Analysis Table ==========
stride_threshold = 0.45 * height_m
step_width_min = 0.043 * height_m * 100
step_width_max = 0.074 * height_m * 100

thresholds = {
    'gait_speed': {'good': 1.12},
    'stride_length': {'good': stride_threshold},
    'step_width': {'min': step_width_min, 'max': step_width_max},
    'cadence': {'good': 100},
    'double_support_time': {'good': 35},
    'step_length_symmetry': {'min': 90, 'max': 110}
}

def classify(metric, value):
    if metric == 'gait_speed':
        return 'within normal gait range' if value >= thresholds[metric]['good'] else 'low'
    elif metric == 'stride_length':
        return 'within normal gait range' if value >= thresholds[metric]['good'] else 'low'
    elif metric == 'step_width':
        return 'within normal gait range' if thresholds[metric]['min'] <= value * 100 <= thresholds[metric]['max'] else 'high'
    elif metric == 'cadence':
        return 'within normal gait range' if value >= thresholds[metric]['good'] else 'low'
    elif metric == 'double_support_time':
        return 'within normal gait range' if value < thresholds[metric]['good'] else 'high'
    elif metric == 'step_length_symmetry':
        return 'within normal gait range' if thresholds[metric]['min'] <= value <= thresholds[metric]['max'] else 'asymmetric'

metric_display = {
    'gait_speed': 'Gait speed (m/s)',
    'stride_length': 'Stride length (m)',
    'step_width': 'Step width (cm)',
    'cadence': 'Cadence (steps/min)',
    'double_support_time': 'Double support time (%)',
    'step_length_symmetry': 'Step length symmetry (%, R/L)'
}

summary = {
    'Metric': [],
    'Value': [],
    'Recommended': [],
    'Status': []
}

for key in metric_display:
    display = metric_display[key]
    val = avg_metrics[key]['value'] * 100 if key == 'step_width' else avg_metrics[key]['value']
    if key == 'stride_length':
        recommended = f">= {thresholds[key]['good']:.2f} m"
    elif key == 'step_width':
        recommended = f"{thresholds[key]['min']:.1f}-{thresholds[key]['max']:.1f} cm"
    elif key == 'step_length_symmetry':
        recommended = f"{thresholds[key]['min']}-{thresholds[key]['max']}"
    elif key == 'double_support_time':
        recommended = f"< {thresholds[key]['good']}"
    else:
        recommended = f">= {thresholds[key]['good']}"

    status = classify(key, val / 100 if key == 'step_width' else val)

    summary['Metric'].append(display)
    summary['Value'].append(round(val, 2))
    summary['Recommended'].append(recommended)
    summary['Status'].append(status)

df_summary = pd.DataFrame(summary)

output_dir = os.path.join(sessionDir, 'Gait_Analysis_Output')
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, 'gait_summary_table.csv')
df_summary.to_csv(output_path, index=False)
print(f"\n✅ Gait metric summary saved to: {output_path}")

# Set OpenSim GUI executable path
opensim_gui_path = r"C:\OpenSim 4.5\bin\OpenSim64.exe"  # Adjust if needed

# Get full paths to model and motion file
model_path = os.path.join(sessionDir, 'OpenSimData', 'Model', 'LaiUhlrich2022_scaled.osim')
mot_path = os.path.join(sessionDir, 'OpenSimData', 'Kinematics', f'{trialName}.mot')

# Launch OpenSim GUI with the model
subprocess.Popen([opensim_gui_path, model_path])

print("\nOpenSim GUI launched with model:")
print(model_path)
print("Please manually load the motion file in the GUI:")
print(mot_path)