import pandas as pd

def count_labels(csv_path):
    try:
        df = pd.read_csv(csv_path)

        if 'label' not in df.columns:
            raise ValueError("CSV must contain a 'label' column.")

        label_counts = df['label'].value_counts()

        print("Label distribution:")
        for label in ['ai', 'human']:
            count = label_counts.get(label, 0)
            print(f"   - {label.upper()}: {count} rows")

        print(f"Total rows: {len(df)}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    count_labels("data/train.csv") 
