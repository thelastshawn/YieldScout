def get_custom_css(is_light_mode):
    if is_light_mode:
        # LIGHT MODE (Soft Grey Background, Dark Text)
        return """
        <style>
            .stApp { background-color: #F3F4F6 !important; }
            [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #D1D5DB; }
            [data-testid="metric-container"] {
                background-color: #D3D3D3 !important; 
                border: 1px solid #10B981; border-left: 5px solid #10B981; 
                padding: 15px 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); 
            }
            h1, h2, h3, h4, h5, h6, p, label, div, span, .stMarkdown { color: #1F2937 !important; font-family: 'Inter', sans-serif; }
            .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
                background-color: #FFFFFF !important; color: #1F2937 !important; border: 1px solid #D1D5DB !important; font-weight: bold;
            }
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-weight: bold; color: #6B7280 !important; }
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] [data-testid="stMarkdownContainer"] p { color: #10B981 !important; }
            .property-card { background-color: #FFFFFF; padding: 10px; border-radius: 8px; border: 1px solid #D1D5DB; margin-bottom: 15px; }
            .profit-text { color: #059669 !important; font-weight: bold; font-size: 1.2em; }
            .pagination-text { text-align: center; color: #4B5563 !important; font-size: 1.0em; padding-bottom: 5px; }
            .disclaimer { font-size: 0.8em; color: #9CA3AF !important; font-style: italic; margin-top: 10px;}
        </style>
        """
    else:
        # DARK MODE (Institutional Quant)
        return """
        <style>
            .stApp { background-color: #0B0F19 !important; }
            [data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid #1F2937; }
            [data-testid="metric-container"] {
                background-color: #1F2937 !important; 
                border: 1px solid #10B981; border-left: 5px solid #10B981; 
                padding: 15px 20px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5); 
            }
            h1, h2, h3, h4, h5, h6, p, label, div, span, .stMarkdown { color: #F8FAFC !important; font-family: 'Inter', sans-serif; }
            .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
                background-color: #111827 !important; color: #10B981 !important; border: 1px solid #374151 !important; font-weight: bold;
            }
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-weight: bold; color: #9CA3AF !important; }
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] [data-testid="stMarkdownContainer"] p { color: #10B981 !important; }
            .property-card { background-color: #1F2937; padding: 10px; border-radius: 8px; border: 1px solid #374151; margin-bottom: 15px; }
            .profit-text { color: #10B981 !important; font-weight: bold; font-size: 1.2em; }
            .pagination-text { text-align: center; color: #9CA3AF !important; font-size: 1.0em; padding-bottom: 5px; }
            .disclaimer { font-size: 0.8em; color: #6B7280 !important; font-style: italic; margin-top: 10px;}
        </style>
        """
