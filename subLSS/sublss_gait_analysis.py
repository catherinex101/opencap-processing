r'''
    ---------------------------------------------------------------------------
    OpenCap processing: sublss_gait_analysis.py
    ---------------------------------------------------------------------------
    Copyright 2023 Stanford University and the Authors

    Author(s): Scott Uhlrich, modified by Catherine
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
sys.path.append("../")
sys.path.append("../ActivityAnalyses")

from gait_analysis import gait_analysis
from utils import get_trial_id, download_trial
from utilsPlotting import plot_dataframe_with_shading

# %% Paths.
baseDir = os.path.join(os.getcwd(), '..')
dataFolder = os.path.join(baseDir, 'Data')

# %% User-defined variables.
example = 'overground'

scalar_names = {'gait_speed','stride_length','step_width','cadence',
                'single_support_time','double_support_time','step_length_symmetry'}

n_gait_cycles = 3
filter_frequency = 6

# Set local session path and trial name manually
sessionDir = r"C:\Users\cxiang\Documents\GitHub\opencap-processing\Data\sub-LSSPilot\OpenCapData_532c118d-a51c-4b8b-9528-7c70ddf4fddb"
trialName = "10_m_walk"

# === Load metadata for height and mass ===
metadata_path = os.path.join(sessionDir, 'sessionMetadata.yaml')
with open(metadata_path, 'r') as f:
    metadata = yaml.safe_load(f)

height_m = metadata['height_m']
mass_kg = metadata['mass_kg']

# Init gait analysis.
gait_r = gait_analysis(
    sessionDir, trialName, leg='r',
    lowpass_cutoff_frequency_for_coordinate_values=filter_frequency,
    n_gait_cycles=n_gait_cycles)
gait_l = gait_analysis(
    sessionDir, trialName, leg='l',
    lowpass_cutoff_frequency_for_coordinate_values=filter_frequency,
    n_gait_cycles=n_gait_cycles)

# Compute scalars and get time-normalized kinematic curves.
gaitResults = {}
gaitResults['scalars_r'] = gait_r.compute_scalars(scalar_names)
gaitResults['curves_r'] = gait_r.get_coordinates_normalized_time()
gaitResults['scalars_l'] = gait_l.compute_scalars(scalar_names)
gaitResults['curves_l'] = gait_l.get_coordinates_normalized_time()

# Print scalar results.
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

# Plot normalized curves.
plot_dataframe_with_shading(
    [gaitResults['curves_r']['mean'], gaitResults['curves_l']['mean']],
    [gaitResults['curves_r']['sd'], gaitResults['curves_l']['sd']],
    leg = ['r','l'],
    xlabel = '% gait cycle',
    title = 'kinematics (m or deg)',
    legend_entries = ['right','left'])

# === Compute average values across both legs ===
avg_metrics = {}
for key in scalar_names:
    if key == 'step_length_symmetry':
        avg_metrics[key] = gaitResults['scalars_r'][key]  # Only use right side
        continue
    val_r = gaitResults['scalars_r'][key]['value']
    val_l = gaitResults['scalars_l'][key]['value']
    unit = gaitResults['scalars_r'][key]['units']
    avg_metrics[key] = {'value': (val_r + val_l) / 2, 'units': unit}

# === Define thresholds for classification ===
stride_threshold = 0.45 * height_m
step_width_min = 0.043 * height_m * 100  # convert to cm
step_width_max = 0.074 * height_m * 100  # convert to cm

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

# === Build gait analysis table for export ===
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

# === Save to folder inside session directory ===
output_dir = os.path.join(sessionDir, 'PilotAnalysis_4_21_25')
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, 'gait_summary_table.csv')
df_summary.to_csv(output_path, index=False)
print(f"\n✅ Gait metric summary saved to: {output_path}")
