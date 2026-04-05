import streamlit as st
import math
import plotly.express as px

# Import the logic from our other files!
from api import fetch_property_gallery_api
from styles import get_custom_css

st.set_page_config(page_title="YieldScout™ | Investor Engine", layout="wide")

# --- STATE MANAGEMENT ---
if 'property_results' not in st.session_state:
    st.session_state['property_results'] = []
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 0

# --- LIGHT/DARK MODE TOGGLE ---
st.sidebar.markdown("### ⚙️ App Settings")
is_light_mode = st.sidebar.toggle("☀️ Enable Light Mode", value=False)
st.markdown(get_custom_css(is_light_mode), unsafe_allow_html=True)
st.sidebar.divider()

# --- HEADER & SLOGAN ---
st.title("📈 YieldScout™")
st.subheader("Real Estate ROI & Cap Rate Analyzer")
st.caption("🔒 Institutional-grade math for real estate wholesalers and buy-and-hold investors.")

# --- ZONE 1: INVESTMENT PARAMETERS (Sidebar) ---
st.sidebar.header("📊 Investment Parameters")

with st.sidebar.expander("💼 Revenue & Expenses", expanded=True):
    est_monthly_rent = st.number_input("Est. Monthly Rent ($)", value=3500, step=100)
    rehab_budget = st.number_input("Est. Rehab Budget ($)", value=15000, step=5000)
    vacancy_rate = st.slider("Vacancy Rate (%)", 0.0, 15.0, 5.0, 0.5) / 100
    management_fee = st.slider("Property Mgmt Fee (%)", 0.0, 15.0, 8.0, 0.5) / 100

with st.sidebar.expander("🏦 Financing Terms", expanded=True):
    down_payment_pct = st.slider("Down Payment %", 0.0, 1.0, 0.20, 0.01)
    interest_rate = st.number_input("Interest Rate (%)", value=6.500, step=0.125, format="%.3f") / 100
    loan_term_years = st.selectbox("Amortization (Years)", [30, 15, 20, 10], index=0)

with st.sidebar.expander("🏡 Filter MLS Data", expanded=True):
    # REFINED FILTERS: Sleek drop-downs instead of clunky +/- buttons
    beds_selection = st.selectbox("Minimum Bedrooms", ["1+", "2+", "3+", "4+", "5+"], index=2)
    baths_selection = st.selectbox("Minimum Bathrooms", ["1+", "2+", "3+", "4+"], index=1)
    
    # Strip the "+" to pass a clean integer to the API
    min_beds = int(beds_selection.replace("+", ""))
    min_baths = int(baths_selection.replace("+", ""))
    
    min_sqft = st.number_input("Minimum SqFt", value=1200, step=100)
    max_hoa_fee = st.number_input("Max Monthly HOA ($)", value=400, step=50)

# --- ZONE 3: THE INVESTOR DASHBOARD (Pop-Up) ---
@st.dialog("📈 Investment Pro Forma", width="large")
def show_dashboard(prop):
    target_price = prop['price']
    target_taxes = prop['taxes']
    target_hoa = prop['hoa']
    
    st.markdown(f"### 🏢 **{prop['address']}** | {prop['type']}")
    if prop['images']: st.image(prop['images'], width=150) 
    
    # 1. Income & Expenses
    gross_annual_rent = est_monthly_rent * 12
    annual_vacancy_loss = gross_annual_rent * vacancy_rate
    annual_management_cost = gross_annual_rent * management_fee
    annual_taxes = target_taxes * 12 if target_taxes > 0 else (target_price * 0.012)
    annual_hoa = target_hoa * 12
    annual_insurance = target_price * 0.005 
    
    total_operating_expenses = annual_taxes + annual_insurance + annual_hoa + annual_vacancy_loss + annual_management_cost
    net_operating_income = gross_annual_rent - total_operating_expenses
    
    # 2. Debt Service
    down_payment_amount = target_price * down_payment_pct
    loan_amount = target_price - down_payment_amount
    total_cash_invested = down_payment_amount + rehab_budget
    
    r = interest_rate / 12
    total_months = loan_term_years * 12
    monthly_pi = loan_amount * (r * (1 + r)**total_months) / ((1 + r)**total_months - 1) if loan_amount > 0 else 0
    annual_debt_service = monthly_pi * 12
    
    # 3. Returns
    annual_cash_flow = net_operating_income - annual_debt_service
    monthly_cash_flow = annual_cash_flow / 12
    cap_rate = (net_operating_income / target_price) * 100 if target_price > 0 else 0
    cash_on_cash = (annual_cash_flow / total_cash_invested) * 100 if total_cash_invested > 0 else 0
    
    # DISPLAY METRICS
    st.divider()
    st.markdown("#### Return Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cap Rate", f"{cap_rate:.2f}%")
    col2.metric("Cash-on-Cash Return", f"{cash_on_cash:.2f}%")
    col3.metric("Net Operating Income", f"${net_operating_income:,.0f}/yr")
    col4.metric("Monthly Cash Flow", f"${monthly_cash_flow:,.0f}")

    st.divider()
    st.markdown("#### Capital Required (Out of Pocket)")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric(f"Down Pmt ({down_payment_pct*100:.0f}%)", f"${down_payment_amount:,.0f}")
    col_b.metric("Est. Rehab Budget", f"${rehab_budget:,.0f}")
    col_c.metric("Total Cash Needed", f"${total_cash_invested:,.0f}")

    st.markdown('<p class="disclaimer">Disclaimer: Projections are based on user estimates and public data. Do not use for official underwriting.</p>', unsafe_allow_html=True)

# --- ZONE 2: SMART SEARCH TABS ---
tab1, tab2 = st.tabs(["🌐 MLS Arbitrage Scanner", "✏️ Manual Deal Entry"])

with tab1:
    # FIXED SEARCH ALIGNMENT
    st.markdown("**Target Zip Code:**")
    col1, col2 = st.columns([3, 1])
    # The 'label_visibility="collapsed"' pushes the text box down to align with the button perfectly!
    zip_input = col1.text_input("Target Zip Code:", value="92117", label_visibility="collapsed")
    
    if col2.button("🔍 Scan Area", use_container_width=True):
        with st.spinner("Compiling investment targets..."):
            results = fetch_property_gallery_api(zip_input, min_beds, min_baths, min_sqft, max_hoa_fee)
            if results:
                st.session_state['property_results'] = results
                st.session_state['current_page'] = 0 
            else:
                st.error("No properties found matching these parameters.")

    if st.session_state['property_results']:
        st.divider()
        col_title, col_sort = st.columns([2, 1])
        col_title.markdown("### 🏢 Available Inventory")
        
        def update_sort():
            st.session_state['current_page'] = 0 
            
        sort_option = col_sort.selectbox("Sort By:", ["Newest Listing", "Price: Low to High", "Price: High to Low"], on_change=update_sort)
        
        display_results = st.session_state['property_results']
        if sort_option == "Price: Low to High": display_results = sorted(display_results, key=lambda x: x['price'])
        elif sort_option == "Price: High to Low": display_results = sorted(display_results, key=lambda x: x['price'], reverse=True)
        
        ITEMS_PER_PAGE = 12 
        total_items = len(display_results)
        total_pages = math.ceil(total_items / ITEMS_PER_PAGE)
        
        if st.session_state['current_page'] >= total_pages: st.session_state['current_page'] = 0
            
        start_idx = st.session_state['current_page'] * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        page_results = display_results[start_idx:end_idx]
        
        cols = st.columns(4)
        for idx, prop in enumerate(page_results): 
            with cols[idx % 4]: 
                # FIXED PROPERTY BUBBLE: Using native Streamlit containers instead of messy HTML divs
                with st.container(border=True):
                    st.image(prop['images'][0], use_container_width=True) 
                    st.markdown(f"<span class='profit-text'>${prop['price']:,.0f}</span>", unsafe_allow_html=True)
                    st.caption(f"{prop['address']}")
                    
                    if st.button("📊 Run Math", key=f"btn_{prop['address']}", use_container_width=True):
                        show_dashboard(prop)
                
        # --- PAGINATION CONTROLS ---
        st.divider()
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        
        if col_prev.button("⬅️ Previous", disabled=(st.session_state['current_page'] == 0), use_container_width=True):
            st.session_state['current_page'] -= 1
            st.rerun()
            
        def handle_page_jump():
            selected_page = st.session_state['page_jumper_select']
            st.session_state['current_page'] = selected_page - 1
            
        col_page.markdown(f"<div class='pagination-text'><b>{total_items}</b> properties found</div>", unsafe_allow_html=True)
        
        page_numbers = list(range(1, total_pages + 1))
        col_page.selectbox(
            "Jump to page:", 
            options=page_numbers, 
            index=st.session_state['current_page'],
            key="page_jumper_select", 
            on_change=handle_page_jump,
            label_visibility="collapsed"
        )
        
        if col_next.button("Next ➡️", disabled=(st.session_state['current_page'] >= total_pages - 1), use_container_width=True):
            st.session_state['current_page'] += 1
            st.rerun()

with tab2:
    st.markdown("### ✏️ Manual Deal Entry")
    st.caption("Underwrite an off-market or wholesale deal manually.")
    col_a, col_b, col_c = st.columns(3)
    manual_price = col_a.number_input("Purchase Price ($)", value=0.0, step=10000.0)
    manual_taxes = col_b.number_input("Monthly Taxes ($)", value=0.0, step=100.0)
    manual_hoa = col_c.number_input("Monthly HOA ($)", value=0.0, step=50.0)
    
    if st.button("📊 Analyze Off-Market Deal", use_container_width=True):
        if manual_price > 0:
            mock_prop = {
                'price': manual_price,
                'taxes': manual_taxes,
                'hoa': manual_hoa,
                'address': "Off-Market Target",
                'type': "Manual Entry",
                'images': []
            }
            show_dashboard(mock_prop)
