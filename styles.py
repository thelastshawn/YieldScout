def get_custom_css(is_light_mode):
    if is_light_mode:
        # LIGHT MODE
        return """
        <style>
            .stApp { background-color: #F9FAFB !important; color: #111827 !important; }
            [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E5E7EB; }
            [data-testid="metric-container"] {
                background-color: #FFFFFF !important; 
                border: 1px solid #10B981; border-left: 5px solid #10B981; 
                padding: 15px 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); 
            }
            .profit-text { color: #059669 !important; font-weight: bold; font-size: 1.2em; }
            .pagination-text { text-align: center; color: #6B7280; font-size: 1.0em; padding-bottom: 5px; }
            .disclaimer { font-size: 0.8em; color: #9CA3AF !important; font-style: italic; margin-top: 10px;}
        </style>
        """
    else:
        # DARK MODE (Institutional Quant)
        return """
        <style>
            .stApp { background-color: #0B0F19 !important; color: #F8FAFC !important; }
            [data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid #1F2937; }
            [data-testid="metric-container"] {
                background-color: #1F2937 !important; 
                border: 1px solid #10B981; border-left: 5px solid #10B981; 
                padding: 15px 20px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5); 
            }
            .profit-text { color: #10B981 !important; font-weight: bold; font-size: 1.2em; }
            .pagination-text { text-align: center; color: #9CA3AF; font-size: 1.0em; padding-bottom: 5px; }
            .disclaimer { font-size: 0.8em; color: #6B7280 !important; font-style: italic; margin-top: 10px;}
        </style>
        """
