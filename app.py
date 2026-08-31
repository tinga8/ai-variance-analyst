import streamlit as st
import pandas as pd

# 1. Page Setup
st.set_page_config(page_title="AI Variance Analyst", page_icon="📊", layout="wide")
st.title("📊 Intelligent Variance Analysis & Automated Commentary")
st.caption("Instantly isolate budget deviations and generate automated management briefs—No API key required.")

# 2. File Attachment Button (Sidebar)
st.sidebar.header("📁 Data Input")
uploaded_file = st.sidebar.file_uploader("Upload your Budget vs Actual CSV", type=["csv"])

# 3. Data Processing Logic
if uploaded_file is not None:
    try:
        # If the user uploads a custom CSV file, load it directly
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("Custom CSV file loaded successfully!")
    except Exception as e:
        st.sidebar.error("Error reading file. Falling back to demo data.")
        uploaded_file = None

# Fallback: Generate safe default demo data if no user file is attached
if uploaded_file is None:
    items = [
        "Revenue - North America", 
        "Revenue - Europe", 
        "Cost of Goods Sold (COGS)", 
        "Marketing Expenses", 
        "R&D Salaries", 
        "Office Rent"
    ]
    budget_vals = [100000, 80000, 50000, 20000, 35000, 12000]
    actual_vals = [112000, 74000, 53000, 19000, 35000, 12000]

    df = pd.DataFrame({
        "Line Item": items,
        "Budgeted ($)": budget_vals,
        "Actual ($)": actual_vals
    })

# 4. Core Calculations
# Ensure required column headers exist before calculating
required_cols = ["Line Item", "Budgeted ($)", "Actual ($)"]
if all(col in df.columns for col in required_cols):
    df["Variance ($)"] = df["Actual ($)"] - df["Budgeted ($)"]
    df["Variance (%)"] = (df["Variance ($)"] / df["Budgeted ($)"]) * 100

    # Materiality Threshold Slider
    st.sidebar.header("⚙️ Settings")
    pct_threshold = st.sidebar.slider("Materiality Cutoff (%)", min_value=1.0, max_value=20.0, value=5.0, step=0.5)

    # Filter deviations
    material_df = df[df["Variance (%)"].abs() >= pct_threshold].copy()

    # 5. Display Dashboard Columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Financial Statement Summary")
        styled_df = df.style.format({
            "Budgeted ($)": "${:,.0f}", "Actual ($)": "${:,.0f}",
            "Variance ($)": "${:+,.0f}", "Variance (%)": "{:+,.1f}%"
        })
        st.dataframe(styled_df, use_container_width=True)

    with col2:
        st.subheader("🚨 Material Deviations")
        st.write(f"Items exceeding the **{pct_threshold}%** threshold:")
        if not material_df.empty:
            for _, row in material_df.iterrows():
                color = "green" if row["Variance ($)"] >= 0 else "red"
                if "Cost" in row["Line Item"] or "Expense" in row["Line Item"]:
                    color = "red" if row["Variance ($)"] >= 0 else "green"
                    
                percentage_text = f"{row['Variance (%)']:.1f}%"
                st.markdown(f"**{row['Line Item']}**: :{color}[{percentage_text}]")
        else:
            st.write("No items exceed the current threshold setting.")

    # 6. Automated Intelligence Commentary Engine
    st.subheader("🤖 Automated Management Commentary")

    if st.button("Generate Executive Briefing", type="primary"):
        commentaries = []
        if not material_df.empty:
            for _, row in material_df.iterrows():
                item, var_pct, var_val = row["Line Item"], row["Variance (%)"], row["Variance ($)"]
                is_revenue = "Revenue" in item or "Sales" in item
                is_expense = "Cost" in item or "Expense" in item or "Rent" in item or "Salary" in item
                
                if is_revenue and var_pct > 0:
                    brief = f"🟢 **{item}** outpaced budget expectations by **{var_pct:.1f}%** (+${var_val:,.0f}). This favorable variance indicates stronger-than-anticipated market demand and improved sales conversion rates."
                elif is_revenue and var_pct < 0:
                    brief = f"🔴 **{item}** missed targeted budget markers by **{var_pct:.1f}%** (${var_val:,.0f}). This contraction signals intensifying competitive headwinds or delayed client onboarding cycles."
                elif is_expense and var_pct > 0:
                    brief = f"⚠️ **{item}** exceeded budgeted allocations by **{var_pct:.1f}%** (+${var_val:,.0f}). This cost overrun marks an unfavorable budget breach, likely driven by macroeconomic inflation or unexpected vendor price adjustments."
                elif is_expense and var_pct < 0:
                    brief = f"🟢 **{item}** achieved structural cost savings of **{var_pct:.1f}%** (${var_val:,.0f}). This efficient variance stems from proactive operational optimizations or deferred project timelines."
                else:
                    brief = f"🔍 **{item}** shifted by **{var_pct:.1f}%** (${var_val:,.0f})."
                commentaries.append(brief)
                
            st.info("\n\n".join(commentaries))
        else:
            st.success("All metrics are tracking beautifully within your budget thresholds. No commentary necessary!")
else:
    st.error("Uploaded CSV format is incorrect. Please ensure your columns are named exactly: 'Line Item', 'Budgeted ($)', and 'Actual ($)'.")
