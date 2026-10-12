


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io


st.set_page_config(
    page_title="Student Performance Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Student Performance Analyzer")
st.write("Upload student marks to analyze academic performance.")

# CSV upload
uploaded_file = st.file_uploader(
    "Upload your student marks CSV file",
    type=["csv"]
)

# Use uploaded data or sample data
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read the CSV file: {e}")
        st.stop()
else:
    st.info("Using sample data. Upload a CSV file to analyze your own data.")
    df = pd.DataFrame({
        "Student": [
            "Aarav", "Priya", "Rahul", "Ananya", "Vikram",
            "Sneha", "Arjun", "Meera", "Kiran", "Diya"
        ],
        "Maths": [85, 92, 67, 88, 55, 78, 95, 73, 61, 90],
        "Science": [90, 89, 72, 94, 60, 82, 91, 80, 65, 93],
        "English": [78, 95, 75, 90, 58, 85, 88, 76, 70, 96]
    })

# Validate uploaded data
if df.empty:
    st.error("The CSV file has no rows.")
    st.stop()

df.columns = df.columns.str.strip()

if "Student" not in df.columns:
    st.error("Your CSV must contain a column named 'Student'.")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

# Treat every column except Student as a subject
subjects = [col for col in df.columns if col != "Student"]

if not subjects:
    st.error("Your CSV must contain at least one subject column.")
    st.stop()

# Convert marks to numeric values
for subject in subjects:
    df[subject] = pd.to_numeric(df[subject], errors="coerce")

if df[subjects].isna().any().any():
    st.warning("Some marks are missing or non-numeric. Check your CSV file.")

if ((df[subjects] < 0) | (df[subjects] > 100)).any().any():
    st.error("Marks must be between 0 and 100.")
    st.stop()

# Calculate results
df["Total"] = df[subjects].sum(axis=1, min_count=1)
df["Percentage"] = (
    df["Total"] / (len(subjects) * 100) * 100
).round(2)

df["Result"] = df["Percentage"].apply(
    lambda x: "Pass" if pd.notna(x) and x >= 40 else "Fail"
)

# Sidebar filters
st.sidebar.header("Dashboard Filters")

selected_subject = st.sidebar.selectbox(
    "Select subject",
    subjects
)

search_name = st.sidebar.text_input("Search student")

filtered_df = df[
    df["Student"].astype(str).str.contains(
        search_name, case=False, na=False
    )
]

# Metrics
st.subheader("📌 Performance Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Students", len(filtered_df))
c2.metric(
    "Average Percentage",
    f"{filtered_df['Percentage'].mean():.1f}%"
    if not filtered_df.empty else "N/A"
)
c3.metric(
    "Highest Percentage",
    f"{filtered_df['Percentage'].max():.1f}%"
    if not filtered_df.empty else "N/A"
)
c4.metric(
    "Pass Rate",
    f"{filtered_df['Result'].eq('Pass').mean() * 100:.0f}%"
    if not filtered_df.empty else "N/A"
)

# Charts
st.subheader(f"📈 {selected_subject} Marks")

chart_data = filtered_df[["Student", selected_subject]].dropna()

if not chart_data.empty:
    st.bar_chart(chart_data.set_index("Student"))
else:
    st.info("No marks available for this filter.")

# 📊 Feature 7: Subject-wise Performance Comparison
st.divider()
st.header("📊 Subject-wise Performance Comparison")

# Calculate average marks for each subject
subject_averages = df[subjects].mean().round(2)

# Display average marks as a chart
st.subheader("Average Marks in Each Subject")
st.bar_chart(subject_averages, y_label="Average Marks")

# Display the subject with the highest and lowest average
if not subject_averages.dropna().empty:
    best_subject = subject_averages.idxmax()
    lowest_subject = subject_averages.idxmin()

    col1, col2 = st.columns(2)

    col1.metric(
        "🏆 Best Performing Subject",
        best_subject,
        f"{subject_averages[best_subject]:.2f} average marks"
    )

    col2.metric(
        "📉 Subject Needing Improvement",
        lowest_subject,
        f"{subject_averages[lowest_subject]:.2f} average marks"
    )

# Show exact averages in a table
st.subheader("Subject Average Details")

average_table = subject_averages.rename("Average Marks").reset_index()
average_table.columns = ["Subject", "Average Marks"]

st.dataframe(average_table, use_container_width=True, hide_index=True)

# 🏆 Top 5 Student Leaderboard
st.divider()
st.subheader("🏆 Top 5 Student Leaderboard")

# Rank students by percentage, highest first
leaderboard = (
    df.dropna(subset=["Percentage"])
    .sort_values(
        by="Percentage",
        ascending=False,
        kind="stable"
    )
    .head(5)
    .copy()
)

if leaderboard.empty:
    st.info("No student results are available for ranking.")
else:
    # Display the highest performer
    top_student = leaderboard.iloc[0]

    st.success(
        f"🥇 Top Performer: {top_student['Student']} "
        f"— {top_student['Percentage']:.2f}%"
    )

    # Add rank numbers
    leaderboard.insert(
        0,
        "Rank",
        range(1, len(leaderboard) + 1)
    )

    # Select useful columns
    display_columns = [
        "Rank",
        "Student",
        "Total",
        "Percentage",
        "Result"
    ]

    st.dataframe(
        leaderboard[display_columns],
        use_container_width=True,
        hide_index=True
    )

    # Visualize the top 5
    st.subheader("📊 Top 5 Students by Percentage")

    chart_data = leaderboard.set_index("Student")["Percentage"]
    st.bar_chart(chart_data, y_label="Percentage (%)")



# 👩‍🎓 Student Results with Color Highlights
st.subheader("👩‍🎓 Student Results")

def highlight_result(row):
    if row["Result"] == "Pass":
        return ["background-color: #d4edda"] * len(row)
    else:
        return ["background-color: #f8d7da"] * len(row)

styled_df = filtered_df.style.apply(highlight_result, axis=1)

st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Download
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download Analyzed Results",
    data=csv_data,
    file_name="student_results.csv",
    mime="text/csv"
)

# 📥 Download Excel Report
import io

excel_buffer = io.BytesIO()

with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    filtered_df.to_excel(
        writer,
        sheet_name="Student Results",
        index=False
    )

    leaderboard.to_excel(
        writer,
        sheet_name="Top 5 Leaderboard",
        index=False
    )

st.download_button(
    label="📥 Download Excel Report",
    data=excel_buffer.getvalue(),
    file_name="student_performance_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 🎓 Feature 8: Individual Student Report
st.divider()
st.header("🎓 Individual Student Report")

student_names = df["Student"].dropna().astype(str).unique().tolist()

if student_names:
    selected_student = st.selectbox(
        "Select a student",
        student_names,
        key="individual_student_report"
    )

    student_report = df[
        df["Student"].astype(str) == selected_student
    ].iloc[0]

    st.subheader(f"📋 Report for {selected_student}")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Marks", f"{student_report['Total']:.0f}")
    col2.metric("Percentage", f"{student_report['Percentage']:.2f}%")
    col3.metric("Result", student_report["Result"])

    st.subheader("📚 Subject-wise Marks")

    subject_report = pd.DataFrame({
        "Subject": subjects,
        "Marks": [student_report[subject] for subject in subjects]
    })

    st.bar_chart(
        subject_report.set_index("Subject"),
        y_label="Marks out of 100"
    )

    st.dataframe(
        subject_report,
        use_container_width=True,
        hide_index=True
    )

    # Download this student's report
    report_csv = pd.DataFrame([student_report]).to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Individual Student Report",
        data=report_csv,
        file_name=f"{selected_student}_report.csv",
        mime="text/csv",
        key="individual_report_download"
    )
else:
    st.info("No student names are available in the data.")

# 📉 Feature 9: Identify Weak Students and Subjects
st.divider()
st.header("📉 Students Needing Support")

support_threshold = st.slider(
    "Minimum expected student percentage",
    min_value=0,
    max_value=100,
    value=60,
    step=5
)

# Find students below the selected percentage
students_needing_support = df[
    df["Percentage"] < support_threshold
].sort_values("Percentage", ascending=True)

st.subheader(
    f"Students scoring below {support_threshold}%"
)

if students_needing_support.empty:
    st.success("Great! No students are below this threshold.")
else:
    st.warning(
        f"{len(students_needing_support)} student(s) may need extra support."
    )

    st.dataframe(
        students_needing_support[
            ["Student", "Total", "Percentage", "Result"]
        ],
        use_container_width=True,
        hide_index=True
    )

# Identify subjects with low class averages
st.subheader("📚 Subjects Needing Improvement")

subject_averages_support = df[subjects].mean()

weak_subjects = subject_averages_support[
    subject_averages_support < support_threshold
].sort_values()

if weak_subjects.empty:
    st.success(
        "No subject averages are below the selected threshold."
    )
else:
    st.dataframe(
        weak_subjects.rename("Average Marks")
        .reset_index()
        .rename(columns={"index": "Subject"}),
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "These thresholds are indicators for review, not definitive judgments "
    "of a student's ability."
)

# Feature 12: Interactive Subject Filter
st.divider()
st.header("📊 Interactive Subject Comparison")

selected_subjects = st.multiselect(
    "Choose subjects to compare",
    options=subjects,
    default=subjects,
    key="interactive_subject_filter"
)

if selected_subjects:
    # Calculate averages for selected subjects
    selected_averages = df[selected_subjects].mean().round(2)

    st.subheader("Average Marks Comparison")
    st.bar_chart(
        selected_averages,
        y_label="Average Marks out of 100"
    )

    # Show selected subject averages
    comparison_table = (
        selected_averages
        .rename("Average Marks")
        .reset_index()
    )
    comparison_table.columns = ["Subject", "Average Marks"]

    st.dataframe(
        comparison_table,
        use_container_width=True,
        hide_index=True
    )

    # Find the highest average among selected subjects
    valid_averages = selected_averages.dropna()

    if not valid_averages.empty:
        best_subject = valid_averages.idxmax()
        st.success(
            f"🏆 Highest average: {best_subject} "
            f"({valid_averages[best_subject]:.2f} marks)"
        )
else:
    st.info("Please select at least one subject to compare.")

# Feature 13: Download Subject Comparison Chart as PNG
st.divider()
st.header("📸 Download Charts as Images")

if subjects:
    fig, ax = plt.subplots(figsize=(8, 5))

    subject_averages = df[subjects].mean()
    subject_averages.plot(kind="bar", ax=ax)

    ax.set_title("Average Marks by Subject")
    ax.set_xlabel("Subject")
    ax.set_ylabel("Average Marks out of 100")
    ax.set_ylim(0, 100)
    ax.tick_params(axis="x", rotation=0)

    fig.tight_layout()

    image_buffer = io.BytesIO()
    fig.savefig(
        image_buffer,
        format="png",
        dpi=150,
        bbox_inches="tight"
    )
    image_buffer.seek(0)

    st.pyplot(fig)

    st.download_button(
        label="⬇️ Download Subject Comparison Chart (PNG)",
        data=image_buffer.getvalue(),
        file_name="subject_comparison_chart.png",
        mime="image/png",
        key="download_subject_chart_png"
    )

    plt.close(fig)
else:
    st.info("No subjects are available to create a chart.")

# Feature 14: Download Subject Statistics as CSV
st.divider()
st.header("📥 Download Subject Statistics")

subject_statistics = pd.DataFrame({
    "Subject": subjects,
    "Average Marks": [df[s].mean() for s in subjects],
    "Highest Marks": [df[s].max() for s in subjects],
    "Lowest Marks": [df[s].min() for s in subjects]
})

subject_statistics = subject_statistics.round(2)

st.subheader("📊 Subject Statistics Table")
st.dataframe(
    subject_statistics,
    use_container_width=True,
    hide_index=True
)

statistics_csv = subject_statistics.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Subject Statistics (CSV)",
    data=statistics_csv,
    file_name="subject_statistics.csv",
    mime="text/csv",
    key="download_subject_statistics_csv"
)

# Feature 15: Student Performance Distribution
st.divider()
st.header("📊 Student Performance Distribution")

# Group students by percentage range
performance_ranges = [
    "0–39%",
    "40–59%",
    "60–79%",
    "80–100%"
]

performance_counts = [
    ((df["Percentage"] >= 0) & (df["Percentage"] < 40)).sum(),
    ((df["Percentage"] >= 40) & (df["Percentage"] < 60)).sum(),
    ((df["Percentage"] >= 60) & (df["Percentage"] < 80)).sum(),
    ((df["Percentage"] >= 80) & (df["Percentage"] <= 100)).sum()
]

distribution_df = pd.DataFrame({
    "Percentage Range": performance_ranges,
    "Number of Students": performance_counts
})

st.bar_chart(
    distribution_df.set_index("Percentage Range"),
    y_label="Number of Students"
)

st.subheader("Distribution Details")
st.dataframe(
    distribution_df,
    use_container_width=True,
    hide_index=True
)

# Feature 16: Student Marks Trend Analysis
st.divider()
st.header("📈 Student Marks Trend Analysis")

student_names = df["Student"].dropna().astype(str).unique().tolist()

if student_names:
    trend_student = st.selectbox(
        "Choose a student to view marks",
        student_names,
        key="marks_trend_student"
    )

    trend_row = df[
        df["Student"].astype(str) == trend_student
    ].iloc[0]

    trend_df = pd.DataFrame({
        "Subject": subjects,
        "Marks": [trend_row[subject] for subject in subjects]
    }).dropna()

    if not trend_df.empty:
        st.line_chart(
            trend_df.set_index("Subject"),
            y_label="Marks out of 100"
        )

        st.dataframe(
            trend_df,
            use_container_width=True,
            hide_index=True
        )

        best = trend_df.loc[trend_df["Marks"].idxmax()]
        lowest = trend_df.loc[trend_df["Marks"].idxmin()]

        col1, col2 = st.columns(2)
        col1.metric(
            "🏆 Highest Subject",
            best["Subject"],
            f"{best['Marks']:.1f} marks"
        )
        col2.metric(
            "📚 Subject to Improve",
            lowest["Subject"],
            f"{lowest['Marks']:.1f} marks"
        )
    else:
        st.info("No subject marks are available for this student.")
else:
    st.info("No students are available.")
# 📌 Performance Summary
st.divider()
st.header("📌 Class Performance Summary")

total_students = len(df)
average_percentage = df["Percentage"].mean()
highest_percentage = df["Percentage"].max()

pass_count = (df["Result"] == "Pass").sum()
fail_count = (df["Result"] == "Fail").sum()

pass_rate = (
    pass_count / total_students * 100
    if total_students > 0 else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("👩‍🎓 Total Students", total_students)
col2.metric("📊 Class Average", f"{average_percentage:.2f}%")
col3.metric("🏆 Highest Score", f"{highest_percentage:.2f}%")
col4.metric("✅ Pass Rate", f"{pass_rate:.1f}%")

st.write(f"**Students passed:** {pass_count}")
st.write(f"**Students failed:** {fail_count}")

# 📊 Pass/Fail Analysis
st.subheader("📊 Pass/Fail Analysis")

result_counts = pd.Series({
    "Pass": pass_count,
    "Fail": fail_count
})

st.bar_chart(result_counts, y_label="Number of Students")

st.divider()

# Feature 10: Download Class Performance PDF
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

st.divider()
st.header("Download Class Performance PDF")

pdf_buffer = io.BytesIO()

styles = getSampleStyleSheet()
pdf = SimpleDocTemplate(
    pdf_buffer,
    pagesize=landscape(A4),
    rightMargin=30,
    leftMargin=30,
    topMargin=30,
    bottomMargin=30
)

elements = []

elements.append(Paragraph("Student Performance Report", styles["Title"]))
elements.append(Spacer(1, 12))

# Class summary
total_students = len(df)
average_percentage = df["Percentage"].mean()
pass_count = (df["Result"] == "Pass").sum()
fail_count = (df["Result"] == "Fail").sum()

summary_data = [
    ["Class Summary", "Value"],
    ["Total Students", str(total_students)],
    ["Average Percentage", f"{average_percentage:.2f}%"],
    ["Students Passed", str(pass_count)],
    ["Students Failed", str(fail_count)]
]

summary_table = Table(summary_data, colWidths=[220, 180])
summary_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("PADDING", (0, 0), (-1, -1), 7),
]))
elements.append(summary_table)
elements.append(Spacer(1, 18))

# Subject averages
elements.append(Paragraph("Subject Averages", styles["Heading2"]))

subject_data = [["Subject", "Average Marks"]]
for subject in subjects:
    avg = df[subject].mean()
    subject_data.append([
        str(subject),
        f"{avg:.2f}" if pd.notna(avg) else "N/A"
    ])

subject_table = Table(subject_data, colWidths=[220, 180])
subject_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("PADDING", (0, 0), (-1, -1), 6),
]))
elements.append(subject_table)
elements.append(Spacer(1, 18))

# Student results
elements.append(Paragraph("Student Results", styles["Heading2"]))

student_data = [["Student", "Total", "Percentage", "Result"]]

for _, row in df.iterrows():
    student_data.append([
        str(row["Student"]),
        str(row["Total"]) if pd.notna(row["Total"]) else "N/A",
        f"{row['Percentage']:.2f}%"
        if pd.notna(row["Percentage"]) else "N/A",
        str(row["Result"])
    ])

student_table = Table(
    student_data,
    repeatRows=1,
    colWidths=[220, 100, 120, 100]
)
student_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("PADDING", (0, 0), (-1, -1), 5),
]))
elements.append(student_table)

pdf.build(elements)
pdf_buffer.seek(0)

st.download_button(
    label="Download Class Performance PDF",
    data=pdf_buffer.getvalue(),
    file_name="class_performance_report.pdf",
    mime="application/pdf"
)

# Feature 11: Student Performance Prediction
st.divider()
st.header("🔮 Student Performance Prediction")

st.write(
    "Estimate a student's performance category using their current marks."
)

student_names = df["Student"].dropna().astype(str).unique().tolist()

if student_names:
    prediction_student = st.selectbox(
        "Choose a student for prediction",
        student_names,
        key="prediction_student"
    )

    student_row = df[
        df["Student"].astype(str) == prediction_student
    ].iloc[0]

    current_percentage = student_row["Percentage"]

    if pd.isna(current_percentage):
        st.warning("This student's percentage cannot be calculated.")
    else:
        st.metric("Current Percentage", f"{current_percentage:.2f}%")

        if current_percentage >= 80:
            prediction = "High performance"
            advice = "Maintain consistent study habits and continue practicing."
        elif current_percentage >= 60:
            prediction = "Moderate performance"
            advice = "Regular revision and practice may help improve results."
        elif current_percentage >= 40:
            prediction = "Needs improvement"
            advice = "Focus on topics where marks are lower and practice regularly."
        else:
            prediction = "At risk of failing"
            advice = "Review foundational topics and seek additional support."

        st.subheader(f"Estimated Category: {prediction}")
        st.info(advice)

        st.caption(
            "This is a rule-based estimate from current marks, not a "
            "machine-learning forecast of future performance."
        )
else:
    st.info("No student names are available.")
st.caption("Beginner Data Science project built with Python, Pandas and Streamlit.")