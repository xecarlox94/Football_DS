from io import BytesIO
from pathlib import Path

from tqdm.notebook import tqdm
from zipfile import ZipFile, is_zipfile

import pandas as pd

from urllib.parse import urlparse
from urllib.request import urlopen, urlretrieve

from sklearn.metrics import brier_score_loss, roc_auc_score
from xgboost import XGBClassifier

import socceraction.vaep.features as features
import socceraction.vaep.labels as labels

from socceraction.spadl.wyscout import convert_to_spadl
from socceraction.vaep.formula import value

import warnings
warnings.filterwarnings('ignore', category=pd.io.pytables.PerformanceWarning)


data_files = {
    'events': 'https://ndownloader.figshare.com/files/14464685',
    'matches': 'https://ndownloader.figshare.com/files/14464622',
    'players': 'https://ndownloader.figshare.com/files/15073721',
    'teams': 'https://ndownloader.figshare.com/files/15073697'
}


for url in tqdm(data_files.values()):
    url_s3 = urlopen(url).geturl()
    path = Path(urlparse(url_s3).path)
    file_name = path.name
    file_local, _ = urlretrieve(url_s3, file_name)
    if is_zipfile(file_local):
        with ZipFile(file_local) as zip_file:
            zip_file.extractall()