import streamlit as st
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Page Configuration & Header
st.set_page_config(page_title="AI Variance Analyst", page_icon="📊", layout="wide")
st.title("📊 Intelligent Variance Analysis Tool")
st.caption("Isolate core budget variations and instantly generate professional PDF management briefs.")

# 2. Setup Internal Enterprise Testing Data
items = [
    "Enterprise Cloud Revenue", 
    "APAC Regional Sales", 
    "Data Center Infrastructure", 
    "Global Marketing Campaigns", 
    "Executive & Legal Payroll", 
    "HQ Facilities & Utilities"
]

budget_vals = [2500000, 1200000, 900000, 350000, 600000, 150000]
actual_vals = [2850000, 1050000, 1300000, 315000, 605000, 148500]

raw_enterprise_df = pd.DataFrame({
    "Line Item": items,
    "Budgeted ($)": budget_vals,
    "Actual ($)": actual_vals
})

# 3. Sidebar Panel: Downloads & Upload Handling
st.sidebar.header("📁 Step 1: Input Data Source")

# Internal background spreadsheet compiler for quick workspace downloads
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    raw_enterprise_df.to_excel(writer, index=False, sheet_name="Variance Sheet")
excel_data = excel_buffer.getvalue()

st.sidebar.download_button(
    label="📥 Download Test Excel Template File",
    data=excel_data,
    file_name="complicated_enterprise_variance.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.sidebar.write("---")

# Main upload entry point (Only takes structured tables)
uploaded_file = st.sidebar.file_uploader("Upload Budget vs Actual (CSV or Excel Format Only)", type=["csv", "xlsx"])

# Route dataset parsing structure based on source state
df = None
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        st.sidebar.success("Custom spreadsheet loaded successfully!")
    except Exception as e:
        st.sidebar.error("Error reading document format. Defaulting to internal ledger layout.")
        df = raw_enterprise_df.copy()
else:
    df = raw_enterprise_df.copy()

# 4. Processing Core Variance Pipelines
required_cols = ["Line Item", "Budgeted ($)", "Actual ($)"]
if all(col in df.columns for col in required_cols):
    df["Variance ($)"] = df["Actual ($)"] - df["Budgeted ($)"]
    df["Variance (%)"] = (df["Variance ($)"] / df["Budgeted ($)"]) * 100

    # Section Settings Configuration Controls
    st.sidebar.header("⚙️ Step 2: Set Materiality Rule")
    pct_threshold = st.sidebar.slider("Materiality Cutoff (%)", min_value=1.0, max_value=20.0, value=5.0, step=0.5)
    material_df = df[df["Variance (%)"].abs() >= pct_threshold].copy()

    # 5. Build Workspace Dashboard Splits
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Financial Statement Summary Table")
        styled_df = df.style.format({
            "Budgeted ($)": "${:,.0f}", "Actual ($)": "${:,.0f}",
            "Variance ($)": "${:+,.0f}", "Variance (%)": "{:+,.1f}%"
        })
        st.dataframe(styled_df, use_container_width=True)

    with col2:
        st.subheader("🚨 Identified Anomalies & Material Flags")
        st.write(f"Line records crossing your assigned variance filter threshold criteria (>{pct_threshold}%):")
        if not material_df.empty:
            for _, row in material_df.iterrows():
                color = "green" if row["Variance ($)"] >= 0 else "red"
                if any(x in row["Line Item"] for x in ["Cost", "Expense", "Costs", "Payroll", "Infrastructure", "Utilities"]):
                    color = "red" if row["Variance ($)"] >= 0 else "green"
                    
                percentage_text = f"{row['Variance (%)']:.1f}%"
                st.markdown(f"**{row['Line Item']}**: :{color}[{percentage_text}]")
        else:
            st.write("No operational items found matching your filter boundary restrictions.")

    st.write("---")

    # 6. Corporate Automation Briefing Layout Section
    st.subheader("🤖 Step 3: Executive Reporting Suite")
    st.write("Process variations to unlock high-impact management commentaries and download your formal PDF corporate document report below.")

    # Initialize workspace memory slots
    if 'saved_commentary' not in st.session_state:
        st.session_state['saved_commentary'] = ""
    if 'pdf_text_list' not in st.session_state:
        st.session_state['pdf_text_list'] = []

    # Run analysis engine processing pipeline triggers
    if st.button("🚀 Process Variations & Generate Corporate Briefing", type="primary"):
        commentaries = []
        raw_text_for_pdf = []
        
        if not material_df.empty:
            for _, row in material_df.iterrows():
                item, var_pct, var_val = row["Line Item"], row["Variance (%)"], row["Variance ($)"]
                is_expense = any(x in item for x in ["Cost", "Expense", "Costs", "Payroll", "Infrastructure", "Utilities"])
                
                if not is_expense and var_pct > 0:
                    brief = f"🟢 **{item}**: Outpaced target expectations by **{var_pct:.1f}%** (+${var_val:,.0f}). This variance indicates stronger strategic market capture and enhanced segment pipeline metrics."
                    pdf_brief = f"• {item}: Outpaced target expectations by {var_pct:.1f}% (+${var_val:,.0f}). This variance indicates stronger strategic market capture and enhanced segment pipeline metrics."
                elif not is_expense and var_pct < 0:
                    brief = f"🔴 **{item}**: Missed performance milestones by **{var_pct:.1f}%** (${var_val:,.0f}). This signals potential execution headwinds or market contract cycle lags."
                    pdf_brief = f"• {item}: Missed performance milestones by {var_pct:.1f}% (${var_val:,.0f}). This signals potential execution headwinds or market contract cycle lags."
                elif is_expense and var_pct > 0:
                    brief = f"⚠️ **{item}**: Expanded above initial allocations by **{var_pct:.1f}%** (+${var_val:,.0f}). This expenditure expansion marks an unfavorable budget breach, suggesting a need to evaluate capacity constraints or supplier cost terms."
                    pdf_brief = f"• {item}: Expanded above initial allocations by {var_pct:.1f}% (+${var_val:,.0f}). This expenditure expansion marks an unfavorable budget breach, suggesting a need to evaluate capacity constraints or supplier cost terms."
                elif is_expense and var_pct < 0:
                    brief = f"🟢 **{item}**: Achieved run-rate efficiencies of **{var_pct:.1f}%** (${var_val:,.0f}). This operational saving signals proactive internal optimization or structural spending discipline."
                    pdf_brief = f"• {item}: Achieved run-rate efficiencies of {var_pct:.1f}% (${var_val:,.0f}). This operational saving signals proactive internal optimization or structural spending discipline."
                else:
                    brief = f"🔍 **{item}**: Registered a variance deviation of **{var_pct:.1f}%** (${var_val:,.0f})."
                    pdf_brief = f"• {item}: Registered a variance deviation of {var_pct:.1f}% (${var_val:,.0f})."
                
                commentaries.append(brief)
                raw_text_for_pdf.append(pdf_brief)
            
            st.session_state['saved_commentary'] = "\n\n".join(commentaries)
            st.session_state['pdf_text_list'] = raw_text_for_pdf
        else:
            st.session_state['saved_commentary'] = "All data segments track safely within target limitations. No analytical briefing paperwork is required at this checkpoint."
            st.session_state['pdf_text_list'] = ["All data segments track safely within target limitations. No analytical briefing paperwork is required at this checkpoint."]

    # Render commentary content blocks and unlock download widgets seamlessly
    if st.session_state['saved_commentary']:
        st.info(st.session_state['saved_commentary'])
        
        # Assemble standard institutional multi-layered layout files inside runtime memory
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#1A365D"), spaceAfter=12)
        subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#4A5568"), spaceAfter=20)
        body_style = ParagraphStyle('DocBody', parent=styles['Normal'], fontSize=11, leading=16, textColor=colors.HexColor("#2D3748"), spaceAfter=14)
        
        story.append(Paragraph("Automated Variance Analysis Memo", title_style))
        story.append(Paragraph("Corporate Management Briefing & Strategic Narrative Insights", subtitle_style))
        story.append(Spacer(1, 12))
        
        for text in st.session_state['pdf_text_list']:
            story.append(Paragraph(text, body_style))
            
        doc.build(story)
        pdf_data = pdf_buffer.getvalue()
        
        # Display the formal file export download shortcut link action button
        st.download_button(
            label="💾 Download Finished Commentary as PDF Report File",
            data=pdf_data,
            file_name="Management_Variance_Report.pdf",
            mime="application/pdf"
        )
else:
    st.error("Uploaded sheet layout doesn't match required design structure. Set table columns to: 'Line Item', 'Budgeted ($)', 'Actual ($)'.")
