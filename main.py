import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "student_marks.csv"
OUTPUT_DIR = BASE_DIR / "outputs"

# Passing mark for each subject
PASS_MARK = 35
def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 1. Read the dataset
    df = pd.read_csv(DATA_FILE)

    subjects = [
        "math", "science", "english", "social", "computer"
    ]

    # 2. Validate the data
    if df.empty:
        print("The dataset is empty.")
        return

    if df[subjects].isnull().any().any():
        print("Missing marks found. Please check the CSV file.")
        return

    if not df[subjects].apply(
        lambda col: col.between(0, 100).all()
    ).all():
        print("Marks must be between 0 and 100.")
        return

    # 3. Calculate total marks and percentage
    df["total_marks"] = df[subjects].sum(axis=1)
    df["percentage"] = (
        df["total_marks"] / (len(subjects) * 100) * 100
    ).round(2)

    # 4. Determine pass/fail status
    df["result"] = df[subjects].ge(PASS_MARK).all(axis=1).map(
        {True: "Pass", False: "Needs Improvement"}
    )

    # 5. Calculate subject-wise averages
    subject_averages = df[subjects].mean().round(2)

    # 6. Identify the topper
    topper = df.loc[df["total_marks"].idxmax()]

    # 7. Display summary
    print("\n===== STUDENT PERFORMANCE ANALYZER =====")
    print("Total students:", len(df))
    print("Total subjects:", len(subjects))

    print(
        f"Class average: {df['percentage'].mean():.2f}%"
    )

    print(
        f"Topper: {topper['student_name']}"
        f" - {topper['percentage']:.2f}%"
    )

    print(
        "Students passing every subject:",
        (df["result"] == "Pass").sum()
    )

    print("\nSubject-wise average marks:")
    print(subject_averages.to_string())

    print("\nStudent results:")
    print(
        df[["student_name", "total_marks",
            "percentage", "result"]]
        .sort_values("percentage", ascending=False)
        .to_string(index=False)
    )

    # 8. Save results to CSV
    results_file = OUTPUT_DIR / "student_results.csv"

    df.sort_values(
        "percentage", ascending=False
    ).to_csv(results_file, index=False)

    print("\nResults saved to:", results_file)

    # 9. Create a subject-wise bar chart
    plt.figure(figsize=(9, 5))
    subject_averages.sort_values(
        ascending=False
    ).plot(kind="bar")

    plt.title("Average Marks by Subject")
    plt.xlabel("Subject")
    plt.ylabel("Average Marks")
    plt.ylim(0, 100)
    plt.xticks(rotation=0)
    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "subject_averages.png")
    plt.show()
    plt.close()

    # 10. Create a percentage distribution histogram
    plt.figure(figsize=(9, 5))
    plt.hist(df["percentage"], bins=6, edgecolor="black")

    plt.title("Distribution of Student Percentages")
    plt.xlabel("Percentage")
    plt.ylabel("Number of Students")
    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "percentage_distribution.png")
    plt.show()
    plt.close()

    print("\nCharts saved successfully!")


if __name__ == "__main__":
    main()