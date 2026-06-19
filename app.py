import streamlit as st
import json
import pandas as pd
import io

# 1. Page Configuration
st.set_page_config(
    page_title="LeadForge",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Mock Data
@st.cache_data
def load_data():
    try:
        with open("mock_leads.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback if run from a different directory
        with open("leadforge/mock_leads.json", "r") as f:
            return json.load(f)

leads_data = load_data()

# Initialize Session State
if "industry_filter" not in st.session_state:
    st.session_state.industry_filter = []
if "size_filter" not in st.session_state:
    st.session_state.size_filter = (50, 500)
if "funding_filter" not in st.session_state:
    st.session_state.funding_filter = []
if "location_filter" not in st.session_state:
    st.session_state.location_filter = []
if "selected_company" not in st.session_state:
    st.session_state.selected_company = None
if "edited_emails" not in st.session_state:
    st.session_state.edited_emails = {}

# Reset Callback
def reset_filters():
    st.session_state.industry_filter = []
    st.session_state.size_filter = (50, 500)
    st.session_state.funding_filter = []
    st.session_state.location_filter = []
    st.session_state.selected_company = None

# Custom CSS styling for premium card aesthetics
st.markdown("""
<style>
    .lead-card-container {
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e9ecef;
    }
    .lead-card-high {
        border-left: 6px solid #28a745;
    }
    .lead-card-medium {
        border-left: 6px solid #fd7e14;
    }
    .lead-card-low {
        border-left: 6px solid #dc3545;
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 6px;
        text-transform: uppercase;
    }
    .badge-high { background-color: #d4edda; color: #155724; }
    .badge-medium { background-color: #fff3cd; color: #856404; }
    .badge-low { background-color: #f8d7da; color: #721c24; }
    .badge-industry { background-color: #e2e8f0; color: #4a5568; }
    .badge-location { background-color: #e0f2fe; color: #0369a1; }
    .badge-status { background-color: #f3e8ff; color: #6b21a8; }
    .card-title {
        font-size: 20px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
    }
    .signal-text {
        font-size: 13px;
        color: #475569;
        background-color: #ffffff;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px dashed #cbd5e1;
        margin-top: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

try:
    st.image("assets/leadforge_banner.png", use_container_width=True)
except Exception:
    pass

# Helper function to get location match key
def get_location_key(loc_str):
    if "India" in loc_str:
        return "India"
    elif "USA" in loc_str:
        return "USA"
    elif "Singapore" in loc_str:
        return "Singapore"
    else:
        return "Global"

# Filter Logic (computed globally so CSV export / counts are always correct)
filtered_leads = []
for lead in leads_data:
    # Industry check
    if st.session_state.industry_filter and lead["industry"] not in st.session_state.industry_filter:
        continue
    # Size check
    if not (st.session_state.size_filter[0] <= lead["employee_count"] <= st.session_state.size_filter[1]):
        continue
    # Funding check
    if st.session_state.funding_filter and lead["funding_stage"] not in st.session_state.funding_filter:
        continue
    # Location check
    if st.session_state.location_filter:
        loc_key = get_location_key(lead["location"])
        if loc_key not in st.session_state.location_filter:
            continue
    filtered_leads.append(lead)

# Sort leads by fit score descending
filtered_leads = sorted(filtered_leads, key=lambda x: x["fit_score"], reverse=True)

# =====================================================================
# SCREEN 1 — Sidebar: ICP Configuration (conditional contents)
# =====================================================================
st.sidebar.title("ICP Configuration")

if not st.session_state.selected_company:
    industry_options = ["B2B SaaS", "Fintech", "DevTools", "Data Infrastructure", "Sales Intelligence"]
    selected_industries = st.sidebar.multiselect(
        "Target Industries",
        options=industry_options,
        key="industry_filter"
    )

    selected_size = st.sidebar.slider(
        "Company Size (Employees)",
        min_value=10,
        max_value=5000,
        value=st.session_state.size_filter,
        step=10,
        key="size_filter"
    )

    funding_options = ["Seed", "Series A", "Series B", "Series C", "Public"]
    selected_funding = st.sidebar.multiselect(
        "Funding Stage",
        options=funding_options,
        key="funding_filter"
    )

    location_options = ["India", "USA", "Singapore", "Global"]
    selected_locations = st.sidebar.multiselect(
        "Location",
        options=location_options,
        key="location_filter"
    )

    st.sidebar.button("Reset Filters", on_click=reset_filters, use_container_width=True)
    st.sidebar.markdown(f"**Showing {len(filtered_leads)} of 15 leads**")
else:
    st.sidebar.markdown(f"Currently viewing details for **{st.session_state.selected_company}**.")
    if st.sidebar.button("← Back to Lead Queue", key="sidebar_back", use_container_width=True):
        st.session_state.selected_company = None
        st.rerun()

# =====================================================================
# MAIN LAYOUT RENDERING
# =====================================================================
if not st.session_state.selected_company:
    # =====================================================================
    # SCREEN 2 — Main Panel: Lead Research Queue
    # =====================================================================
    st.title("LeadForge — Lead Research Queue")

    # Subtitle showing active ICP filter summary
    industry_summary = ", ".join(st.session_state.industry_filter) if st.session_state.industry_filter else "All"
    funding_summary = ", ".join(st.session_state.funding_filter) if st.session_state.funding_filter else "All"
    loc_summary = ", ".join(st.session_state.location_filter) if st.session_state.location_filter else "All"
    st.markdown(
        f"Active ICP: **Industry**: {industry_summary} | **Size**: {st.session_state.size_filter[0]}-{st.session_state.size_filter[1]} | **Funding**: {funding_summary} | **Location**: {loc_summary}"
    )

    # Metric row at top of main queue
    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    total_shown = len(filtered_leads)
    avg_score = int(sum(l["fit_score"] for l in filtered_leads) / total_shown) if total_shown > 0 else 0
    high_count = sum(1 for l in filtered_leads if l["fit_level"] == "High")
    med_count = sum(1 for l in filtered_leads if l["fit_level"] == "Medium")
    low_count = sum(1 for l in filtered_leads if l["fit_level"] == "Low")

    col_m1.metric("Leads Shown", total_shown)
    col_m2.metric("Avg Fit Score", f"{avg_score}%")
    col_m3.metric("High Fit", high_count)
    col_m4.metric("Medium Fit", med_count)
    col_m5.metric("Low Fit", low_count)

    st.write("---")

    # Render cards
    for idx, lead in enumerate(filtered_leads):
        level = lead["fit_level"].lower()
        fit_color = "#28a745" if lead["fit_score"] >= 70 else ("#fd7e14" if lead["fit_score"] >= 40 else "#dc3545")
        
        card_col1, card_col2 = st.columns([5, 1])
        
        with card_col1:
            st.markdown(f"""
            <div class="lead-card-container lead-card-{level}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span class="card-title">{lead['company_name']}</span>
                    <div>
                        <span class="badge badge-industry">{lead['industry']}</span>
                        <span class="badge badge-location">📍 {lead['location']}</span>
                        <span class="badge badge-status">Status: {lead['status']}</span>
                        <span class="badge badge-{level}">{lead['fit_level']} Fit</span>
                    </div>
                </div>
                <div><strong>Top Signal:</strong></div>
                <div class="signal-text">📣 {lead['recent_news'][0]}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with card_col2:
            st.write("") # vertical spacing alignment
            st.write("")
            st.markdown(f"<div style='text-align: center; font-weight: bold; color: {fit_color}; font-size: 24px;'>{lead['fit_score']}%</div>", unsafe_allow_html=True)
            st.progress(lead["fit_score"] / 100.0)
            
            # Details button
            if st.button("View Details →", key=f"details_{lead['company_name']}_{idx}", use_container_width=True):
                st.session_state.selected_company = lead["company_name"]
                st.rerun()

    # =====================================================================
    # SCREEN 4 — Analytics Footer (Rendered on Home Queue Page)
    # =====================================================================
    st.write("---")
    st.subheader("Analytics Dashboard")

    col_a1, col_a2, col_a3, col_a4 = st.columns(4)

    total_leads = len(leads_data)
    global_avg_score = int(sum(l["fit_score"] for l in leads_data) / total_leads)
    global_high_fit = sum(1 for l in leads_data if l["fit_level"] == "High")
    hours_saved = round(total_leads * 0.75)

    col_a1.metric("Total Leads Researched", total_leads)
    col_a2.metric("Avg Fit Score (All)", f"{global_avg_score}%")
    col_a3.metric("High Fit Leads (All)", global_high_fit)
    col_a4.metric("Est. Hours Saved", f"~{hours_saved} hrs")

    # Prepare distribution bar chart
    low_dist = sum(1 for l in filtered_leads if l["fit_score"] < 40)
    med_dist = sum(1 for l in filtered_leads if 40 <= l["fit_score"] < 70)
    high_dist = sum(1 for l in filtered_leads if l["fit_score"] >= 70)

    dist_df = pd.DataFrame({
        "Fit Level": ["Low (<40)", "Medium (40-69)", "High (>=70)"],
        "Lead Count": [low_dist, med_dist, high_dist]
    }).set_index("Fit Level")

    st.write("#### Fit Score Distribution of Filtered Leads")
    st.bar_chart(dist_df)

    # CSV Export Button
    export_rows = []
    for lead in filtered_leads:
        comp_name = lead["company_name"]
        emails = st.session_state.edited_emails.get(comp_name, lead["email_sequence"])
        
        row = {
            "Company Name": lead["company_name"],
            "Website": lead["website"],
            "Industry": lead["industry"],
            "Employee Count": lead["employee_count"],
            "Funding Stage": lead["funding_stage"],
            "Location": lead["location"],
            "Fit Score": lead["fit_score"],
            "Fit Level": lead["fit_level"],
            "Score Reasoning": lead["score_reasoning"],
            "Recent News": "; ".join(lead["recent_news"]),
            "Tech Stack": ", ".join(lead["tech_stack"]),
            "Top Hiring Roles": ", ".join(lead["top_hiring_roles"]),
            "Inferred Pain Points": "; ".join(lead["inferred_pain_points"]),
            "Red Flags": "; ".join(lead["red_flags"]) if lead["red_flags"] else "None",
            "Email Touch 1": emails["touch_1"],
            "Email Touch 2": emails["touch_2"],
            "Email Touch 3": emails["touch_3"],
            "Status": lead["status"]
        }
        export_rows.append(row)

    export_df = pd.DataFrame(export_rows)
    csv_buffer = io.StringIO()
    export_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    st.download_button(
        label="📥 Export Filtered Leads to CSV",
        data=csv_data,
        file_name="leadforge_export.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    # =====================================================================
    # SCREEN 3 — Company Deep-Dive (replaces main queue when selected)
    # =====================================================================
    selected_lead = next((l for l in leads_data if l["company_name"] == st.session_state.selected_company), None)
    
    if selected_lead:
        # Title and Back Button row
        back_col, title_col = st.columns([1, 5])
        with back_col:
            st.write("")  # vertical alignment
            if st.button("← Back to Queue", key="main_back", use_container_width=True):
                st.session_state.selected_company = None
                st.rerun()
        with title_col:
            st.title(f"🔍 Deep-Dive: {selected_lead['company_name']}")
        
        # Header Info Row
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        col_h1.markdown(f"**Website**: [{selected_lead['website']}]({selected_lead['website']})")
        col_h2.markdown(f"**Location**: {selected_lead['location']}")
        col_h3.markdown(f"**Funding Stage**: {selected_lead['funding_stage']}")
        col_h4.markdown(f"**Employee Count**: {selected_lead['employee_count']}")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Intelligence Report")
            
            st.markdown("**Recent News & Signals:**")
            for news in selected_lead["recent_news"]:
                st.markdown(f"- {news}")
            
            st.markdown("**Tech Stack:**")
            tech_html = " ".join([f'<span class="badge badge-industry" style="background-color: #f1f5f9; border: 1px solid #cbd5e1;">{tech}</span>' for tech in selected_lead["tech_stack"]])
            st.markdown(tech_html, unsafe_allow_html=True)
            
            st.markdown("**Top Hiring Roles:**")
            roles_html = " ".join([f'<span class="badge badge-location" style="background-color: #eff6ff; border: 1px solid #bfdbfe;">{role}</span>' for role in selected_lead["top_hiring_roles"]])
            st.markdown(roles_html, unsafe_allow_html=True)
            
            st.markdown("**Inferred Pain Points:**")
            for pain in selected_lead["inferred_pain_points"]:
                st.markdown(f"- ⚠️ {pain}")
                
            if selected_lead["red_flags"]:
                st.markdown("**Red Flags:**")
                for flag in selected_lead["red_flags"]:
                    st.markdown(f"- 🚨 <span style='color: #dc3545;'>{flag}</span>", unsafe_allow_html=True)
            else:
                st.markdown("**Red Flags:** None")
                
        with col_right:
            st.subheader("Fit Score Breakdown")
            
            breakdown = selected_lead["score_breakdown"]
            
            try:
                st.image("assets/score_rubric.jpeg", use_container_width=True)
            except Exception:
                pass
            
            st.write(f"Size Fit: **{breakdown['size_fit']}/25**")
            st.progress(breakdown["size_fit"] / 25.0)
            
            st.write(f"Tech Match: **{breakdown['tech_match']}/25**")
            st.progress(breakdown["tech_match"] / 25.0)
            
            st.write(f"Hiring Velocity: **{breakdown['hiring_velocity']}/25**")
            st.progress(breakdown["hiring_velocity"] / 25.0)
            
            st.write(f"Pain Keyword Match: **{breakdown['pain_keyword_match']}/25**")
            st.progress(breakdown["pain_keyword_match"] / 25.0)
            
            st.markdown(f"**Score Reasoning:**\n\n_{selected_lead['score_reasoning']}_")
            
        st.markdown("### Generated Email Sequence")
        
        comp_name = selected_lead["company_name"]
        if comp_name not in st.session_state.edited_emails:
            st.session_state.edited_emails[comp_name] = {
                "touch_1": selected_lead["email_sequence"]["touch_1"],
                "touch_2": selected_lead["email_sequence"]["touch_2"],
                "touch_3": selected_lead["email_sequence"]["touch_3"]
            }
            
        with st.expander("Touch 1 (Cold Intro - Signal-based)", expanded=True):
            t1_val = st.text_area("Subject & Email Body", value=st.session_state.edited_emails[comp_name]["touch_1"], key=f"t1_{comp_name}", height=150)
            st.session_state.edited_emails[comp_name]["touch_1"] = t1_val
            
        with st.expander("Touch 2 (Value Prop & Social Proof)", expanded=False):
            t2_val = st.text_area("Subject & Email Body", value=st.session_state.edited_emails[comp_name]["touch_2"], key=f"t2_{comp_name}", height=150)
            st.session_state.edited_emails[comp_name]["touch_2"] = t2_val
            
        with st.expander("Touch 3 (Low-pressure Breakup)", expanded=False):
            t3_val = st.text_area("Subject & Email Body", value=st.session_state.edited_emails[comp_name]["touch_3"], key=f"t3_{comp_name}", height=150)
            st.session_state.edited_emails[comp_name]["touch_3"] = t3_val
            
        st.success("Draft edits saved in-session.")

