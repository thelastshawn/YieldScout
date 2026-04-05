import requests
import streamlit as st

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
        "x-rapidapi-key": st.secrets["RAPIDAPI_KEY"], 
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
