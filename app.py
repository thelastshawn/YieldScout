import streamlit as st
import requests
import math
import plotly.express as px

st.set_page_config(page_title="YieldScout™ | Investor Engine", layout="wide")

# --- STATE MANAGEMENT ---
if 'property_results' not in st.session_state:
    st.session_state['property_results'] = []
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 0

# --- CUSTOM CSS INJECTION (INSTITUTIONAL QUANT) ---
custom_css = """
<style>
    .stApp { background-color: #0B0F19 !important; }
    [data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid #1F2937; }
    [data-testid="metric-container"] {
        background-color: #1F2937 !important; 
        border: 1px solid #10B981; border-left: 5px solid #10B981; 
        padding: 15px 20px; border-radius: 8px; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5); 
    }
    h1, h2, h3, h4, h5, h6, p, label, div, span, .stMarkdown {
        color: #F8FAFC !important; font-family: 'Inter', sans-serif;
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #111827 !important; color: #10B981 !important; border: 1px solid #374151 !important; font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-weight: bold; color: #9CA3AF; }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] [data-testid="stMarkdownContainer"] p { color: #10B981; }
    .property-card { background-color: #1F2937; padding: 10px; border-radius: 8px; border: 1px solid #374151; margin-bottom: 15px; transition: 0.3s; }
    .property-card:hover { border-color: #10B981; }
    .disclaimer { font-size: 0.8em; color: #6B7280 !important; font-style: italic; margin-top: 10px;}
    .pagination-text { text-align: center; color: #9CA3AF; font-size: 1.0em; padding-bottom: 5px; }
    .profit-text { color: #10B981 !important; font-weight: bold; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- HEADER & SLOGAN ---
st.title("📈 YieldScout™")
st.subheader("Real Estate ROI & Cap Rate Analyzer")
st.caption("🔒 Institutional-grade math for real estate wholesalers and buy-and-hold investors.")

# --- THE BACKEND: API FETCH ---
def fetch_property_gallery_api(zip_code, beds, baths, min_sqft, max_hoa):
    url = "https://realty-in-us.p.rapidapi.com/properties/v3/list"
    payload = {
        "limit": 100, 
        "offset": 0,
        "postal_code": str(zip_code),
        "status": ["for_sale", "ready_to_build", "pending"], 
        "sort": { "direction": "desc", "field": "list_date" },
        "beds_min": int(beds),
        "baths_min": int(baths),
        "sqft_min": int(min_sqft)
    }
    headers = {
        "x-rapidapi-key": "ad67d0a64dmsh514c74e7fcdc0a0p13b2fbjsnd81dec4f00d5", # Replace with env variable in production
        "x-rapidapi-host": "realty-in-us.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get("data", {}).get("home_search", {}).get("results", [])
            
            parsed_properties = []
            for prop in results:
                price = prop.get("list_price", 0)
                if not price: continue 
                
                hoa = prop.get("description", {}).get("hoa", 0)
                if max_hoa > 0 and (hoa and hoa > max_hoa): continue 
                
                annual_taxes = prop.get("tax_record", {}).get("property_tax", 0)
                monthly_taxes = annual_taxes / 12 if annual_taxes else 0
                address = prop.get("location", {}).get("address", {}).get("line", "Unknown Address")
                home_type = prop.get("description", {}).get("type", "Home").replace("_", " ").title()
                
                photo_list = []
                raw_photos = prop.get("photos", [])
                if raw_photos:
                    photo_list = [p.get("href", "").replace("s.jpg", "od-w1024_h768.webp") for p in raw_photos if p.get("href")]
                else:
                    primary = prop.get("primary_photo", {}).get("href", "")
                    if primary: photo_list.append(primary.replace("s.jpg", "od-w1024_h768.webp"))
                
                parsed_properties.append({
                    'price': float(price),
                    'hoa': float(hoa) if hoa else 0.0,
                    'taxes': float(monthly_taxes),
                    'address': address,
                    'type': home_type,
                    'images': photo_list[:6] if photo_list else ["https://via.placeholder.com/400x300?text=No+Photo"]
                })
            return parsed_properties
        return []
    except Exception as e:
        return []

# --- ZONE 1: INVESTMENT PARAMETERS (Sidebar) ---
st.sidebar.header("📊 Investment Parameters")

with st.sidebar.expander("💼 Revenue & Expenses", expanded=True):
    est_monthly_rent = st.number_input("Est. Monthly Rent ($)", value=3500, step=100, help="Your target gross monthly rental income.")
    rehab_budget = st.number_input("Est. Rehab Budget ($)", value=15000, step=5000, help="Initial cash required for repairs before renting.")
    vacancy_rate = st.slider("Vacancy Rate (%)", 0.0, 15.0, 5.0, 0.5, help="Percentage of the year the property will sit empty.") / 100
    management_fee = st.slider("Property Mgmt Fee (%)", 0.0, 15.0, 8.0, 0.5, help="Fee paid to a property management company.") / 100

with st.sidebar.expander("🏦 Financing Terms", expanded=True):
    down_payment_pct = st.slider("Down Payment %", 0.0, 1.0, 0.20, 0.01)
    interest_rate = st.number_input("Interest Rate (%)", value=6.500, step=0.125, format="%.3f") / 100
    loan_term_years = st.selectbox("Amortization (Years)", [30, 15, 20, 10], index=0)

with st.sidebar.expander("🏡 Filter MLS Data", expanded=True):
    min_beds = st.number_input("Minimum Bedrooms", value=3, step=1)
    min_baths = st.number_input("Minimum Bathrooms", value=2, step=1)
    min_sqft = st.number_input("Minimum SqFt", value=1200, step=100)
    max_hoa_fee = st.number_input("Max Monthly HOA ($)", value=400, step=50)

# --- ZONE 3: THE INVESTOR DASHBOARD (Pop-Up) ---
@st.dialog("📈 Investment Pro Forma", width="large")
def show_dashboard(prop):
    target_price = prop['price']
    target_taxes = prop['taxes']
    target_hoa = prop['hoa']
    
    st.markdown(f"### 🏢 **{prop['address']}** | {prop['type']}")
    
    if prop['images']:
        st.image(prop['images'], width=150) 
    
    # --- CORE INVESTOR MATH ---
    # 1. Income & Expenses
    gross_annual_rent = est_monthly_rent * 12
    annual_vacancy_loss = gross_annual_rent * vacancy_rate
    annual_management_cost = gross_annual_rent * management_fee
    annual_taxes = target_taxes * 12 if target_taxes > 0 else (target_price * 0.012)
    annual_hoa = target_hoa * 12
    annual_insurance = target_price * 0.005 # Estimate 0.5% of value
    
    total_operating_expenses = annual_taxes + annual_insurance + annual_hoa + annual_vacancy_loss + annual_management_cost
    net_operating_income = gross_annual_rent - total_operating_expenses
    
    # 2. Debt Service (Mortgage)
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
    
    # --- DISPLAY METRICS ---
    st.divider()
    st.markdown("#### Return Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cap Rate", f"{cap_rate:.2f}%")
    col2.metric("Cash-on-Cash Return", f"{cash_on_cash:.2f}%")
    col3.metric("Net Operating Income", f"${net_operating_income:,.0f}/yr")
    
    # Color-code cash flow
    if monthly_cash_flow >= 0:
        col4.metric("Monthly Cash Flow", f"${monthly_cash_flow:,.0f}")
    else:
        col4.metric("Monthly Cash Flow", f"-${abs(monthly_cash_flow):,.0f}")

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
    col1, col2 = st.columns([3, 1])
    zip_input = col1.text_input("Target Zip Code:", value="92117")
    
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
        
        # --- 4-COLUMN PAGINATION LOGIC ---
        ITEMS_PER_PAGE = 12 # Switched to 12 to fit a 4x3 grid perfectly
        total_items = len(display_results)
        total_pages = math.ceil(total_items / ITEMS_PER_PAGE)
        
        if st.session_state['current_page'] >= total_pages:
            st.session_state['current_page'] = 0
            
        start_idx = st.session_state['current_page'] * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        page_results = display_results[start_idx:end_idx]
        
        # Switched to a 4-column grid for higher density
        cols = st.columns(4)
        for idx, prop in enumerate(page_results): 
            with cols[idx % 4]: 
                st.markdown('<div class="property-card">', unsafe_allow_html=True)
                st.image(prop['images'][0], use_container_width=True) 
                st.markdown(f"<span class='profit-text'>${prop['price']:,.0f}</span>", unsafe_allow_html=True)
                st.caption(f"{prop['address']}")
                
                if st.button("📊 Run Deal Math", key=f"btn_{prop['address']}", use_container_width=True):
                    show_dashboard(prop)
                st.markdown('</div>', unsafe_allow_html=True)
                
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
