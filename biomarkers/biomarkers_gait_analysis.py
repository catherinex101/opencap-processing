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
from datetime import datetime

sys.path.append("../")
sys.path.append("../ActivityAnalyses")

from gait_analysis import gait_analysis

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

def select_valid_gait_cycle(gait_obj, video_duration_sec, buffer=0.01):
    times = gait_obj.gaitEvents['ipsilateralTime']
    for i in range(len(times)):
        hs1, _, hs2 = times[i]
        if hs2 + buffer <= video_duration_sec:
            print(f"✅ Selected gait cycle index: {i} (HS2 = {hs2:.2f}s)")
            return hs1, hs2, i
    raise ValueError("❌ No valid gait cycle found before video end.")

def process_gait_session(sessionDir):
    trialName = "walk"
    metadata_path = os.path.join(sessionDir, 'sessionMetadata.yaml')
    with open(metadata_path, 'r') as f:
        metadata = yaml.safe_load(f)
    height_m = metadata['height_m']
    
    scalar_names = {'gait_speed','stride_length','step_width','cadence',
                    'single_support_time','double_support_time','step_length_symmetry'}
    filter_frequency = 6
    n_gait_cycles = 2

    video_filename = f"{trialName}_sync.mp4"
    cam1_path = os.path.join(sessionDir, "Videos", "Cam1", "InputMedia", trialName, video_filename)
    cam0_path = os.path.join(sessionDir, "Videos", "Cam0", "InputMedia", trialName, video_filename)
    video_duration_sec = min(get_video_duration(cam1_path), get_video_duration(cam0_path))

    gait_r = gait_analysis(sessionDir, trialName, leg='r',
        lowpass_cutoff_frequency_for_coordinate_values=filter_frequency,
        n_gait_cycles=n_gait_cycles, gait_style='overground')
    hs1_r, hs2_r, idx_r = select_valid_gait_cycle(gait_r, video_duration_sec, buffer=0.3)

    save_cam1_path_r = os.path.join(sessionDir, "Videos", "Cam1", "InputMedia", trialName, f"{trialName}_sync_cropped_r_cycle{idx_r}.mp4")
    save_cam0_path_r = os.path.join(sessionDir, "Videos", "Cam0", "InputMedia", trialName, f"{trialName}_sync_cropped_r_cycle{idx_r}.mp4")
    crop_video_ffmpeg(cam1_path, save_cam1_path_r, hs1_r, hs2_r)
    crop_video_ffmpeg(cam0_path, save_cam0_path_r, hs1_r, hs2_r)

    scalars_r = gait_r.compute_scalars(scalar_names, selected_cycle_index=idx_r)

    gait_l = gait_analysis(sessionDir, trialName, leg='l',
        lowpass_cutoff_frequency_for_coordinate_values=filter_frequency,
        n_gait_cycles=n_gait_cycles, gait_style='overground')
    hs1_l, hs2_l, idx_l = select_valid_gait_cycle(gait_l, video_duration_sec, buffer=0.3)

    save_cam1_path_l = os.path.join(sessionDir, "Videos", "Cam1", "InputMedia", trialName, f"{trialName}_sync_cropped_l_cycle{idx_l}.mp4")
    save_cam0_path_l = os.path.join(sessionDir, "Videos", "Cam0", "InputMedia", trialName, f"{trialName}_sync_cropped_l_cycle{idx_l}.mp4")
    crop_video_ffmpeg(cam1_path, save_cam1_path_l, hs1_l, hs2_l)
    crop_video_ffmpeg(cam0_path, save_cam0_path_l, hs1_l, hs2_l)

    scalars_l = gait_l.compute_scalars(scalar_names, selected_cycle_index=idx_l)

    avg_metrics = {}
    for key in scalar_names:
        if key == 'step_length_symmetry':
            avg_metrics[key] = scalars_r.get(key, {'value': None})
            continue
        val_r = scalars_r.get(key, {}).get('value')
        val_l = scalars_l.get(key, {}).get('value')
        if val_r is not None and val_l is not None:
            avg_metrics[key] = {'value': (val_r + val_l) / 2}

    metric_display = {
        'gait_speed': 'Gait speed (m/s)',
        'stride_length': 'Stride length (m)',
        'step_width': 'Step width (cm)',
        'cadence': 'Cadence (steps/min)',
        'double_support_time': 'Double support time (%)',
        'step_length_symmetry': 'Step length symmetry (%, R/L)'
    }

    data = {}
    for key, display_name in metric_display.items():
        val = avg_metrics[key]['value']
        if key == 'step_width':
            val *= 100
        data[display_name] = [round(val, 2)]

    session_id = os.path.basename(sessionDir).replace("OpenCapData_", "")
    data = {'Opencap Session ID': [session_id]} | data
    df_columns = pd.DataFrame(data)

    output_dir = os.path.join(sessionDir, 'Gait_Analysis_Pass1')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'gait_metrics_pass1.csv')
    df_columns.to_csv(output_path, index=False)
    print(f"\n✅ Gait metrics saved to: {output_path}")

    # Launch OpenSim GUI
    opensim_gui_path = r"C:\OpenSim 4.5\bin\OpenSim64.exe"
    model_path = os.path.join(sessionDir, 'OpenSimData', 'Model', 'LaiUhlrich2022_scaled.osim')
    mot_path = os.path.join(sessionDir, 'OpenSimData', 'Kinematics', f'{trialName}.mot')
    print("\nOpenSim GUI launched with model:")
    print(model_path)
    print("Please manually load the motion file in the GUI:")
    print(mot_path)
    subprocess.run([opensim_gui_path, model_path])

    return df_columns

# ================================
# MAIN — Run one session at a time
# ================================
if __name__ == "__main__":
    sessionDir = r"C:\Users\cxiang\Documents\GitHub\opencap-processing\Data\biomarkers\OpenCapData_73cbe6ea-05b6-4c6b-a522-ab1be0221637"
    base_dir = os.path.dirname(sessionDir)
    compiled_csv_path = os.path.join(base_dir, 'gait_metrics_compiled.csv')
    log_path = os.path.join(base_dir, 'gait_metrics_log.txt')

    try:
        df = process_gait_session(sessionDir)
        session_id = df['Opencap Session ID'].iloc[0]

        # Check for duplicates
        if os.path.exists(compiled_csv_path):
            compiled_df = pd.read_csv(compiled_csv_path)
            if session_id in compiled_df['Opencap Session ID'].values:
                print(f"⚠️ Session {session_id} already exists in compiled CSV. Skipping.")
                with open(log_path, 'a') as logf:
                    logf.write(f"{datetime.now()} — Duplicate session skipped: {session_id}\n")
                sys.exit(0)

        print("\n📊 Summary of extracted metrics:")
        print(df.to_string(index=False))

        approve = input("\n➕ Include this session in master CSV? (y/n): ").strip().lower()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if approve == 'y':
            if os.path.exists(compiled_csv_path):
                master_df = pd.read_csv(compiled_csv_path)
                master_df = pd.concat([master_df, df], ignore_index=True)
            else:
                master_df = df
            master_df.to_csv(compiled_csv_path, index=False)
            print(f"✅ Added to master CSV: {compiled_csv_path}")
            with open(log_path, 'a') as logf:
                logf.write(f"{timestamp} — Included session: {session_id}\n")
        else:
            print("❌ Skipped adding to master CSV.")
            with open(log_path, 'a') as logf:
                logf.write(f"{timestamp} — Skipped session: {session_id}\n")

    except Exception as e:
        print(f"❌ Error processing session: {e}")
        with open(log_path, 'a') as logf:
            logf.write(f"{datetime.now()} — ERROR with session {sessionDir}: {e}\n")
