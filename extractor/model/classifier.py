import pandas as pd
import glob
import os
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.impute import SimpleImputer
import joblib
import matplotlib.pyplot as plt
from xgboost import XGBClassifier

data_dir = "trainingdata/"
all_files = glob.glob(os.path.join(data_dir, "*.csv"))

df_list = [pd.read_csv(file) for file in all_files]
df = pd.concat(df_list, ignore_index=True)
print(f"Loaded {len(df)} rows from {len(all_files)} files.")

required = [
    'heading','content','avgFontSize','height','width','textLength',
    'x0','y0','x1','y1','isBold','isItalic'
]
missing = set(required) - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df['isBold'] = df['isBold'].astype(int)
df['isItalic'] = df['isItalic'].astype(int)

df['avgFontSize'] = df['avgFontSize'].astype(str).str.replace(r'[^\d\.]+', '', regex=True)
df['avgFontSize'] = pd.to_numeric(df['avgFontSize'], errors='coerce')

# Fill missing page number if needed
if 'page' not in df.columns:
    raise ValueError("Missing 'page' column for relative font size features.")

# Document-wide average (excluding NaNs)
doc_mean_font = df['avgFontSize'].mean()

# Page-wise average
df['pageFontMean'] = df.groupby('page')['avgFontSize'].transform('mean')

# Relative font size features
df['relFontSizePage'] = df['avgFontSize'] / df['pageFontMean']
df['relFontSizeDoc'] = df['avgFontSize'] / doc_mean_font

# Replace inf and NaNs from division
df['relFontSizePage'].replace([np.inf, -np.inf], np.nan, inplace=True)
df['relFontSizeDoc'].replace([np.inf, -np.inf], np.nan, inplace=True)

df['textLength'] = df['textLength'].fillna(0)
if (df['textLength'] == 0).any():
    df['textLength'] = df['content'].fillna('').str.len()

# Derived features
df['lineLength'] = (df['x1'] - df['x0']).clip(lower=0)
df['bboxHeight'] = (df['y1'] - df['y0']).clip(lower=0)
df['area'] = df['lineLength'] * df['bboxHeight']
df['xCenter'] = (df['x0'] + df['x1']) / 2.0
df['yCenter'] = (df['y0'] + df['y1']) / 2.0
df['wordCount'] = df['content'].fillna('').str.split().str.len()

features = [
    'avgFontSize',
    'height','width','textLength',
    'x0','y0','x1','y1',
    'lineLength','bboxHeight','area','xCenter','yCenter',
    'isBold','isItalic','wordCount'
]

X = df[features]
X['avgFontSize'] = X['avgFontSize'];
y_raw = df['heading'].astype(str)



print(X.dtypes)

# Handle NaNs
imp = SimpleImputer(strategy='median')
X_imp = imp.fit_transform(X)

print(X.dtypes)

le = LabelEncoder()
y = le.fit_transform(y_raw)

print("Class distribution:")
print(pd.Series(y_raw).value_counts())

X_train, X_test, y_train, y_test = train_test_split(
    X_imp, y, test_size=0.2, stratify=y, random_state=42
)

clf = RandomForestClassifier(
    n_estimators=400,
    max_features='sqrt',
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred, target_names=le.classes_))
print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))

# Save model, encoder, and imputer
joblib.dump(
    {"model": clf, "label_encoder": le, "imputer": imp, "features": features},
    "heading_rf.joblib"
)
print("Saved to heading_rf.joblib")

importances = clf.feature_importances_
features = X.columns

sorted_idx = importances.argsort()[::-1]
top_features = [features[i] for i in sorted_idx[:10]]
top_importances = [importances[i] for i in sorted_idx[:10]]

plt.figure(figsize=(8, 5))
plt.barh(top_features[::-1], top_importances[::-1])
plt.title("Top 10 Feature Importances")
plt.xlabel("Importance")
plt.tight_layout()
plt.show()