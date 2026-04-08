import io
import os
import tempfile
from fpdf import FPDF
import xlsxwriter
import matplotlib.pyplot as plt

# --- 1. THE SELLER PDF BUILDER ---
# Notice we removed "pie_chart_fig" from the parameters
def build_seller_pdf(sale_price, payoff, commission, closing_costs, net_profit):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, "YieldScout | Estimated Net Sheet", ln=True, align='C')
    pdf.ln(5)

    # Table Header
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Itemized Breakdown", border='B', ln=True)

    # Line Items
    pdf.set_font("Arial", '', 12)
    pdf.cell(100, 10, "Gross Sale Price:")
    pdf.cell(50, 10, f"${sale_price:,.2f}", ln=True, align='R')

    pdf.set_text_color(200, 0, 0) # Red for expenses
    pdf.cell(100, 10, "Mortgage Payoff:")
    pdf.cell(50, 10, f"-${payoff:,.2f}", ln=True, align='R')

    pdf.cell(100, 10, "Agent Commissions:")
    pdf.cell(50, 10, f"-${commission:,.2f}", ln=True, align='R')

    pdf.cell(100, 10, "Closing Costs & Concessions:")
    pdf.cell(50, 10, f"-${closing_costs:,.2f}", ln=True, align='R')

    # Total Profit
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(100, 10, "ESTIMATED NET PROFIT:", border='T')
    pdf.set_text_color(16, 185, 129) # Neon Green for profit
    pdf.cell(50, 10, f"${net_profit:,.2f}", border='T', ln=True, align='R')
    pdf.set_text_color(0, 0, 0)
    
    # --- MATPLOTLIB NATIVE CHART GENERATION ---
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Visual Breakdown:", ln=True, align='C')
    
    # Prep data for the chart
    plot_profit = net_profit if net_profit > 0 else 0 
    sizes = [plot_profit, payoff, commission, closing_costs]
    labels = ["Net Profit", "Mortgage Payoff", "Commissions", "Closing Costs"]
    colors = ['#10B981', '#374151', '#4B5563', '#6B7280']
    
    # Draw the chart without needing a browser
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(sizes, labels=labels, colors=colors, startangle=90, textprops={'color':"w"})
    ax.axis('equal') 
    
    # Save, draw on PDF, and delete
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        plt.savefig(tmpfile.name, format='png', transparent=True, bbox_inches='tight')
        plt.close(fig) # Prevent memory leaks
        pdf.image(tmpfile.name, x=30, y=pdf.get_y(), w=150)
    
    os.remove(tmpfile.name)

    return pdf.output(dest='S').encode('latin1')

# --- 2. THE INVESTOR EXCEL BUILDER ---
# (This remains exactly the same, XlsxWriter is already native and crash-proof)
def build_investor_excel(rent, expenses, debt_service):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    ws = workbook.add_worksheet("10-Year Pro Forma")

    header = workbook.add_format({'bold': True, 'bg_color': '#1F2937', 'font_color': 'white'})
    money = workbook.add_format({'num_format': '$#,##0'})
    bold_money = workbook.add_format({'num_format': '$#,##0', 'bold': True})

    ws.write('A1', 'Metric', header)
    for year in range(1, 11):
        ws.write(0, year, f'Year {year}', header)

    rent_inflation = 0.03
    expense_inflation = 0.02

    metrics = ["Gross Income", "Operating Expenses", "Net Operating Income (NOI)", "Debt Service", "Cash Flow"]
    for row, metric in enumerate(metrics, start=1):
        ws.write(row, 0, metric, header)

    current_rent = rent
    current_exp = expenses

    for year in range(1, 11):
        noi = current_rent - current_exp
        cf = noi - debt_service

        ws.write(1, year, current_rent, money)
        ws.write(2, year, current_exp, money)
        ws.write(3, year, noi, bold_money)
        ws.write(4, year, debt_service, money)
        ws.write(5, year, cf, bold_money)

        current_rent *= (1 + rent_inflation)
        current_exp *= (1 + expense_inflation)

    ws.set_column('A:A', 25)
    ws.set_column('B:K', 15)

    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({
        'name':       'Projected Cash Flow',
        'categories': ['10-Year Pro Forma', 0, 1, 0, 10], 
        'values':     ['10-Year Pro Forma', 5, 1, 5, 10], 
        'fill':       {'color': '#10B981'} 
    })
    
    chart.set_title({'name': '10-Year Cash Flow Projection'})
    chart.set_x_axis({'name': 'Year'})
    chart.set_y_axis({'name': 'Cash Flow ($)'})
    chart.set_size({'width': 700, 'height': 350})
    ws.insert_chart('B8', chart)

    workbook.close()
    output.seek(0)
    return output.read()
