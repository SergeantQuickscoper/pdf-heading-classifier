import argparse
import os
import glob
import pandas as pd
import numpy as np
import joblib
import json


def clean_and_engineer(df):
    df['avgFontSize'] = (
        df['avgFontSize']
        .astype(str)
        .str.replace(r'[^\d\.]+', '', regex=True)
        .replace('', np.nan)
        .astype(float)
    )

    df['isBold'] = df['isBold'].astype(int)
    df['isItalic'] = df['isItalic'].astype(int)
    df['lineLength'] = (df['x1'] - df['x0']).clip(lower=0)
    df['bboxHeight'] = (df['y1'] - df['y0']).clip(lower=0)
    df['area'] = df['lineLength'] * df['bboxHeight']
    df['xCenter'] = (df['x0'] + df['x1']) / 2.0
    df['yCenter'] = (df['y0'] + df['y1']) / 2.0
    df['wordCount'] = df['content'].fillna('').str.split().str.len()
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

    return df

def get_title_from_first_page(df):
    heading_rank = {'H1': 1, 'H2': 2, 'H3': 3, 'BODY': 4}
    df_page1 = df[df['page'] == 1].copy()

    if df_page1.empty:
        return "Untitled Document"

    df_page1['rank'] = df_page1['predicted_heading'].map(heading_rank).fillna(99)
    top = df_page1.sort_values('rank').iloc[0]

    return top['content'].strip()


def build_outline(df):
    title = get_title_from_first_page(df)

    outline = []
    for _, row in df.iterrows():
        level = row['predicted_heading']
        if level in {"H1", "H2", "H3"}:
            outline.append({
                "level": level,
                "text": row['content'].strip(),
                "page": int(row['page']) if 'page' in row and pd.notnull(row['page']) else -1
            })

    return {
        "title": title,
        "outline": outline
    }


def main():
    parser = argparse.ArgumentParser(description="Run heading classifier")
    # CHANGE this as im assuming youre executing from the extractor dir
    parser.add_argument("--model", default="./model/heading_rf.joblib", help="Trained model path")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input PDF or folder containing CSV files"
    )

    args = parser.parse_args()
    bundle = joblib.load(args.model)
    clf = bundle['model']
    le = bundle['label_encoder']
    imp = bundle['imputer']
    features = bundle['features']

    df_list = [pd.read_csv(args.input)]
    df = pd.concat(df_list, ignore_index=True)

    df = clean_and_engineer(df)

    X = df[features].apply(pd.to_numeric, errors='coerce')
    X_imp = imp.transform(X)
    preds = clf.predict(X_imp)
    preds_str = le.inverse_transform(preds)
    df['predicted_heading'] = preds_str

    print(df[['content', 'page', 'predicted_heading']].head())

    outline_json = build_outline(df)
    with open("outline.json", "w", encoding="utf-8") as f:
        json.dump(outline_json, f, indent=4, ensure_ascii=False)

    print("Outline saved to outline.json")


if __name__ == "__main__":
    main()
