import streamlit as st
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Page Setup
st.set_page_config(page_title="AI Variance Analyst", page_icon="📊", layout="wide")
st.title("📊 Intelligent Variance Analysis & Automated Commentary")
st.caption("Instantly isolate budget deviations and generate automated management briefs—No API key required.")

# 2. Complex Mock Enterprise Data Definition
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

# 3. Sidebar Layout Controls & File Generation
st.sidebar.header("📁 Data Input")

# Create a downloadable Excel file block right inside the sidebar memory
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    raw_enterprise_df.to_excel(writer, index=False, sheet_name="Variance Sheet")
excel_data = excel_buffer.getvalue()

# Direct download button for your test spreadsheet file
st.sidebar.download_button(
    label="📥 Download Complex Excel Test File",
    data=excel_data,
    file_name="complicated_enterprise_variance.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.sidebar.write("---")
uploaded_file = st.sidebar.file_uploader("Upload Budget vs Actual (CSV or Excel)", type=["csv", "xlsx"])

# 4. Data Parsing Logic
df = None
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        st.sidebar.success("File uploaded successfully!")
    except Exception as e:
        st.sidebar.error("Error reading file. Using internal fallback layout.")
        df = raw_enterprise_df.copy()
else:
    df = raw_enterprise_df.copy()

# 5. Core Calculations Engine
required_cols = ["Line Item", "Budgeted ($)", "Actual ($)"]
if all(col in df.columns for col in required_cols):
    df["Variance ($)"] = df["Actual ($)"] - df["Budgeted ($)"]
    df["Variance (%)"] = (df["Variance ($)"] / df["Budgeted ($)"]) * 100

    st.sidebar.header("⚙️ Settings")
    pct_threshold = st.sidebar.slider("Materiality Cutoff (%)", min_value=1.0, max_value=20.0, value=5.0, step=0.5)
    material_df = df[df["Variance (%)"].abs() >= pct_threshold].copy()

    # 6. Display Dashboard Columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Financial Summary Ledger")
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
                if any(x in row["Line Item"] for x in ["Cost", "Expense", "Costs", "Payroll", "Infrastructure", "Utilities"]):
                    color = "red" if row["Variance ($)"] >= 0 else "green"
                    
                percentage_text = f"{row['Variance (%)']:.1f}%"
                st.markdown(f"**{row['Line Item']}**: :{color}[{percentage_text}]")
        else:
            st.write("No items exceed the current threshold setting.")

    # 7. Automated Corporate Narrative Commentary
    st.subheader("🤖 Automated Management Commentary")

    if st.button("Generate Executive Briefing", type="primary") or 'saved_commentary' in st.session_state:
        commentaries = []
        raw_text_for_pdf = []
        
        if 'saved_commentary' not in st.session_state:
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
                        brief = f"🔍 **{item}**: Registered a minor variance of **{var_pct:.1f}%** (${var_val:,.0f})."
                        pdf_brief = f"• {item}: Registered a minor variance of {var_pct:.1f}% (${var_val:,.0f})."
                    
                    commentaries.append(brief)
                    raw_text_for_pdf.append(pdf_brief)
                
                st.session_state['saved_commentary'] = "\n\n".join(commentaries)
                st.session_state['pdf_text_list'] = raw_text_for_pdf
            else:
                st.session_state['saved_commentary'] = "All ledgers track within your chosen cutoff matrix limit boundaries. No report required."
                st.session_state['pdf_text_list'] = ["All ledgers track within your chosen cutoff matrix limit boundaries. No report required."]

        # Show commentary on screen
        st.info(st.session_state['saved_commentary'])
        
        # --- PDF Generation Engine ---
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        # Setup clean professional styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor("#1A365D"), spaceAfter=15)
        subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#4A5568"), spaceAfter=25)
        body_style = ParagraphStyle('DocBody', parent=styles['Normal'], fontSize=11, leading=16, textColor=colors.HexColor("#2D3748"), spaceAfter=12)
        
        # Build Document Elements
        story.append(Paragraph("AI-Powered Variance Analysis Report", title_style))
        story.append(Paragraph("Automated Management Commentary & Strategic Briefing Brief", subtitle_style))
        story.append(Spacer(1, 10))
        
        for text in st.session_state['pdf_text_list']:
            story.append(Paragraph(text, body_style))
            
        doc.build(story)
        pdf_data = pdf_buffer.getvalue()
        
        # Render the PDF Download Button
        st.download_button(
            label="💾 Export Commentary as PDF Report",
            data=pdf_data,
            file_name="AI_Management_Commentary.pdf",
            mime="application/pdf"
        )
else:
    st.error("Sheet formatting mismatch. Ensure columns are structured exactly: 'Line Item', 'Budgeted ($)', 'Actual ($)'.")
