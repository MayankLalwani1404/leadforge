# LeadForge — Autonomous B2B Prospect Research & Outreach Engine

## Project Overview
LeadForge is a Streamlit-powered autonomous B2B prospect research and outreach workspace prototype. Designed as a university capstone submission, it models how modern sales development representatives (SDRs) filter leads matching an Ideal Customer Profile (ICP), review intent signals and technographic indicators, customize generative outreach sequences, and track pipeline metrics. This prototype demonstrates premium, modern visual layouts and clean state-management flows using realistic static dataset constraints.

## File Structure
leadforge/
├── app.py - The main Streamlit web application orchestrating the filters, research queue, company deep-dives, email sequence customizers, and analytics visualization.
├── mock_leads.json - A local dataset containing 15 highly realistic B2B SaaS, DevTools, and Fintech company profiles mapped to schema specifications.
└── requirements.txt - Declares application requirements (streamlit and pandas) for environment installations.

## Tech Stack Used
- streamlit: Python web framework for prototyping
- pandas: Dataframe structuring and utility operations for sorting and CSV compilation

## Screens Implemented
1. ICP Configuration Sidebar
- Target Industries multiselect including B2B SaaS, Fintech, DevTools, Data Infrastructure, and Sales Intelligence.
- Company Size range slider filtering company employee counts from 10 to 5000 (default 50-500).
- Funding Stage (Seed, Series A, Series B, Series C, Public) and Location filters (India, USA, Singapore, Global).
- Reset Filters button utilizing st.session_state callbacks to quickly clear values.
- Dynamic lead counter indicating the active number of qualified targets.

2. Main Panel: Lead Research Queue
- Subtitle summarizing active ICP filters dynamically.
- Core metrics displaying overall leads matching criteria, average fit score, and count of High/Medium/Low fits.
- Styled B2B prospect cards rendering company name, industry, location tags, top signals, and a visual progress indicator.
- Fit score colored progress bars highlighting targets green for high (70+), amber for medium (40-69), and red for low (<40).
- View Details action trigger button connecting individual lead profiles to the detail panel.

3. Company Deep-Dive
- Replaces the main queue panel and sidebar filters entirely when a lead is selected to eliminate scrolling latency.
- Actionable back buttons at the top of the deep-dive panel and in the sidebar allowing seamless return to the queue.
- Context header referencing core company metadata including employee size, website link, location, and funding phase.
- Intelligence report panel aggregating news headlines, tech stack listings, open hiring roles, inferred pain points, and red flags.
- Score breakdown visualizer splitting progress values across Size Fit, Tech Match, Hiring Velocity, and Pain Keyword Match (each scaled 0-25).
- Editable email sequence editor displaying touch points (intro, value prop, breakup) in editable text containers with dynamic state updates.

4. Analytics Dashboard Footer
- Global metrics highlighting total leads researched, aggregate average fit score, total high fit leads, and estimated hours saved.
- Fit score distribution bar chart grouping target leads into Low, Medium, and High categories.
- Export to CSV action downloading all active filtered leads including customized emails to leadforge_export.csv.

## Mock Data Summary
The dataset features 15 companies representing real-world SaaS pioneers: Razorpay, Zepto, BrowserStack, Postman, Chargebee, Freshworks, Druva, Mindtickle, Slintel, Uniphore, Hasura, Airbyte, Census, Hightouch, and Segment.
Each record follows this JSON Schema structure:
- company_name: string
- website: string
- industry: string
- employee_count: integer
- funding_stage: string
- location: string
- recent_news: array of strings
- job_postings_count: integer
- top_hiring_roles: array of strings
- tech_stack: array of strings
- inferred_pain_points: array of strings
- fit_score: integer
- score_breakdown: object (size_fit, tech_match, hiring_velocity, pain_keyword_match integers)
- fit_level: string
- score_reasoning: string
- red_flags: array of strings
- email_sequence: object (touch_1, touch_2, touch_3 strings)
- status: string

## Key Design Decisions
- Implemented a dynamic page router: If a company is selected, the application swaps screens to render the deep-dive view and displays a sidebar message; otherwise, it renders the filter panel and lead queue.
- Handled state transitions by mapping select buttons to st.session_state.selected_company and calling st.rerun() to force-refresh panels.
- Preserved email editing text states in a session dictionary (st.session_state.edited_emails) mapping edits back to the company so SDR customizations persist during sessions.
- Injected custom CSS blocks overriding Streamlit styles to render premium card indicators with color-coded left borders matching target priority.
- Constructed a localized parser matching locations against India, USA, Singapore, and Global regions for exact filter alignment.

## How to Run
```bash
streamlit run app.py
```

## Known Limitations
- Static local mock data: No real-time web scraping or external CRM integrations.
- Single-session state persistence: Refreshing the page wipes in-memory email updates and selections.
- Multi-currency simplification: Flat metrics with no active API currency converters.

## Screenshots Checklist
1. Default view showing all 15 leads matching initial parameters.
2. Filtered view showing only Series B companies under the DevTools sector.
3. Company deep-dive displaying detailed analytics for a High-fit lead.
4. Email sequence expander with editable Touch 1 text field.
5. Analytics footer highlighting the bar chart distribution and export button.
