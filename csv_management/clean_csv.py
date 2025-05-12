import pandas as pd
import os

def clean_csv(input_path, output_path):
    try:
        df = pd.read_csv(input_path)

        df.dropna(subset=["text", "label"], inplace=True)

        df = df[df["text"].apply(lambda x: isinstance(x, str))]

        df = df[df["label"].isin(["ai", "human"])]

        df["text"] = df["text"].apply(lambda x: x.strip())

        df.to_csv(output_path, index=False)
        print(f"Cleaned data saved to: {output_path}")
        print(f"Remaining rows: {len(df)}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    INPUT_PATH = os.path.join(BASE_DIR, "data", "train.csv")
    OUTPUT_PATH = os.path.join(BASE_DIR, "data", "train_cleaned.csv")

    clean_csv(INPUT_PATH, OUTPUT_PATH)
