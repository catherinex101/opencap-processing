'''
    ---------------------------------------------------------------------------
    OpenCap processing: batchDownload.py
    ---------------------------------------------------------------------------

    Copyright 2022 Stanford University and the Authors
    
    Author(s): Antoine Falisse, Scott Uhlrich
    Modified by Catherine
    
    Licensed under the Apache License, Version 2.0 (the "License"); you may not
    use this file except in compliance with the License. You may obtain a copy
    of the License at http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

from utils import download_session
import os

# List of sessions you'd like to download. They go to the Data folder in the 
# current directory.
# sessionList = ['7272a71a-e70a-4794-a253-39e11cb7542c',
              # 'abe79267-646f-436b-a19e-a9e1d8f32807']


# Read list of session IDs from CSV column
from pathlib import Path
import pandas as pd
fpath = Path(r'C:\Users\cxiang\Documents\GitHub\opencap-processing\Data\biomarkers\bio_id_to_opencap_session_id.csv')
df = pd.read_csv(fpath)
sessionList = df['opencap_id'].dropna().unique()

             
# base directory for downloads. Specify None if you want to go to os.path.join(os.getcwd(),'Data')
downloadPath = os.path.join(os.getcwd(),'Data/biomarkers')

print("\n📋 Session IDs to be processed:")

for session_id in sessionList:
    # If only interested in marker and OpenSim data, downladVideos=False will be faster
    session_path = os.path.join(downloadPath, f'OpenCapData_{session_id}')
    print(f"- {session_id}")

    if os.path.exists(session_path):
        raise FileExistsError(f"❌ Folder already exists for {session_id}: {session_path}")

    download_session(session_id, sessionBasePath=downloadPath, downloadVideos=True)
