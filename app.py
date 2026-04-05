import streamlit as st
import plotly.express as px
from styles import get_custom_css

st.set_page_config(page_title="YieldScout™ | Underwriting Engine", layout="wide")

# --- LIGHT/DARK MODE TOGGLE ---
st.sidebar.markdown("### ⚙️ App Settings")
is_light_mode = st.sidebar.toggle("☀️ Enable Light Mode", value=False)
st.markdown(get_custom_css(is_light_mode), unsafe_allow_html=True)
st.sidebar.divider()

# --- HEADER & SLOGAN ---
st.title("📈 YieldScout™")
st.subheader("Nationwide Deal Underwriting & Seller Net Profit Calculator")
st.caption("🔒 Institutional-grade math for property sellers and real estate investors.")

# --- TABS ---
tab1, tab2 = st.tabs(["💰 Seller Net Profit Calculator", "📈 Rental ROI Analyzer"])

with tab1:
    st.markdown("### 🏡 Estimate Your Take-Home Profit")
    st.caption("Find out exactly how much cash you'll walk away with after selling your property.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 1. Sale Details")
        sale_price = st.number_input("Expected Sale Price ($)", value=500000, step=10000)
        mortgage_payoff = st.number_input("Remaining Mortgage Balance ($)", value=250000, step=5000)
        
    with col2:
        st.markdown("#### 2. Selling Costs")
        agent_commission_pct = st.slider("Total Agent Commission (%)", 0.0, 10.0, 5.0, 0.5)
        seller_closing_costs = st.number_input("Est. Closing Costs & Concessions ($)", value=5000, step=500)
        
    # Seller Math Logic
    commission_cost = sale_price * (agent_commission_pct / 100)
    total_costs = mortgage_payoff + commission_cost + seller_closing_costs
    net_profit = sale_price - total_costs
    
    st.divider()
    st.markdown("#### 💵 Your Net Proceeds")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sale Price", f"${sale_price:,.0f}")
    c2.metric(f"Commissions ({agent_commission_pct}%)", f"-${commission_cost:,.0f}")
    c3.metric("Mortgage Payoff", f"-${mortgage_payoff:,.0f}")
    c4.metric("Estimated Net Profit", f"${net_profit:,.0f}", delta="Take-Home Cash", delta_color="normal")
    
with tab2:
    st.markdown("### 🏢 Underwrite an Investment Deal")
    st.caption("Calculate Cap Rate, NOI, and Cash-on-Cash Return for a rental property.")
    
    # Grid layout for inputs
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown("#### Acquisition")
        purchase_price = st.number_input("Purchase Price ($)", value=400000, step=10000)
        rehab_budget = st.number_input("Est. Rehab Budget ($)", value=25000, step=5000)
        down_payment_pct = st.slider("Down Payment %", 0.0, 1.0, 0.20, 0.01)
        
    with col_b:
        st.markdown("#### Revenue & Expenses")
        est_monthly_rent = st.number_input("Est. Monthly Rent ($)", value=3500, step=100)
        annual_taxes = st.number_input("Annual Property Taxes ($)", value=4800, step=100)
        annual_insurance = st.number_input("Annual Insurance ($)", value=1200, step=100)
        monthly_hoa = st.number_input("Monthly HOA ($)", value=0, step=50)
        
    with col_c:
        st.markdown("#### Financing Assumptions")
        vacancy_rate = st.slider("Vacancy Rate (%)", 0.0, 15.0, 5.0, 0.5) / 100
        management_fee = st.slider("Property Mgmt Fee (%)", 0.0, 15.0, 8.0, 0.5) / 100
        interest_rate = st.number_input("Interest Rate (%)", value=6.500, step=0.125, format="%.3f") / 100
        loan_term_years = st.selectbox("Amortization (Years)", [30, 15, 20, 10], index=0)
    
    # Investor Math Logic
    gross_annual_rent = est_monthly_rent * 12
    annual_vacancy_loss = gross_annual_rent * vacancy_rate
    annual_management_cost = gross_annual_rent * management_fee
    annual_hoa = monthly_hoa * 12
    
    total_operating_expenses = annual_taxes + annual_insurance + annual_hoa + annual_vacancy_loss + annual_management_cost
    net_operating_income = gross_annual_rent - total_operating_expenses
    
    down_payment_amount = purchase_price * down_payment_pct
    loan_amount = purchase_price - down_payment_amount
    total_cash_invested = down_payment_amount + rehab_budget
    
    r = interest_rate / 12
    total_months = loan_term_years * 12
    monthly_pi = loan_amount * (r * (1 + r)**total_months) / ((1 + r)**total_months - 1) if loan_amount > 0 else 0
    annual_debt_service = monthly_pi * 12
    
    annual_cash_flow = net_operating_income - annual_debt_service
    monthly_cash_flow = annual_cash_flow / 12
    cap_rate = (net_operating_income / purchase_price) * 100 if purchase_price > 0 else 0
    cash_on_cash = (annual_cash_flow / total_cash_invested) * 100 if total_cash_invested > 0 else 0
    
    st.divider()
    
    # DISPLAY METRICS
    st.markdown("#### Return Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Cap Rate", f"{cap_rate:.2f}%")
    m2.metric("Cash-on-Cash Return", f"{cash_on_cash:.2f}%")
    m3.metric("Net Operating Income", f"${net_operating_income:,.0f}/yr")
    
    if monthly_cash_flow >= 0:
        m4.metric("Monthly Cash Flow", f"${monthly_cash_flow:,.0f}", delta="Positive", delta_color="normal")
    else:
        m4.metric("Monthly Cash Flow", f"-${abs(monthly_cash_flow):,.0f}", delta="Negative", delta_color="inverse")
