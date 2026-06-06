import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


COLUMNS = [
    'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs',
    'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target'
]


def load_data(path='data/heart.csv'):
    df = pd.read_csv(path)
    return df


def preprocess(df):
    df = df.copy()

    # UCI Cleveland używa '?' jako brakujące wartości
    df = df.replace('?', np.nan)
    df = df.astype(float)

    # Tylko 'ca' i 'thal' mają braki – uzupełniamy medianą
    df['ca'] = df['ca'].fillna(df['ca'].median())
    df['thal'] = df['thal'].fillna(df['thal'].median())

    # Sprowadzamy target do binarnego: 0 = brak choroby, 1 = choroba
    df['target'] = (df['target'] > 0).astype(int)

    X = df.drop('target', axis=1)
    y = df['target']

    return X, y


def split_and_scale(X, y, test_size=0.2, random_state=42):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train), columns=X.columns, index=X_train.index
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test), columns=X.columns, index=X_test.index
    )

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler
