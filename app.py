import streamlit as st
from PIL import Image
import pandas as pd
import datetime
import os
import random

st.set_page_config(page_title="Mobile Restaurant App", page_icon="🍔", layout="centered")

HISTORY_FILE = "sales_history.csv"
ADMIN_PASSWORD = "admin123"  # உங்களது பாஸ்வேர்ட் 

# Initialize Session State for Restaurant Details
if 'restaurant_name' not in st.session_state:
    st.session_state.restaurant_name = "⭐ அருசுவை உணவகம்"
if 'restaurant_address' not in st.session_state:
    st.session_state.restaurant_address = "12, மெயின் ரோடு, சென்னை - 600001"
if 'restaurant_phone' not in st.session_state:
    st.session_state.restaurant_phone = "9876543210"

# Initialize Session State for Menu Data
if 'menu_data' not in st.session_state:
    st.session_state.menu_data = {
        1: {"item": "Plain Dosa", "price": 50.0, "image": None},
        2: {"item": "Masala Dosa", "price": 70.0, "image": None},
        3: {"item": "Idli (2 Pcs)", "price": 30.0, "image": None},
        4: {"item": "Vada (1 Pc)", "price": 20.0, "image": None}
    }

# Tab Layout Separation
tab1, tab2 = st.tabs(["🍽️ இன்றைய ஆர்டர் (Billing)", "📊 விற்பனை வரலாறு (Admin Only)"])

# --- ADMIN SIDEBAR EDITOR (With Password Lock) ---
st.sidebar.markdown("<h2 style='color: #E67E22;'>🛠️ மேலாளர் பகுதி (Admin)</h2>", unsafe_allow_html=True)
admin_password_input = st.sidebar.text_input("மேலாளர் கடவுச்சொல் (Password):", type="password")

if admin_password_input == ADMIN_PASSWORD:
    st.sidebar.success("🔓 அனுமதி வழங்கப்பட்டது!")
    
    admin_action = st.sidebar.radio("என்ன செய்ய வேண்டும்?", [
        "கடை விபரங்களை மாற்று", 
        "உணவு விலை/படம் மாற்று", 
        "புதிய உணவு சேர் (Add)", 
        "உணவை நீக்கு (Remove)"
    ])

    # 1. Edit Restaurant Info
    if admin_action == "கடை விபரங்களை மாற்று":
        st.sidebar.write("### 🏢 உணவக விபரங்கள்:")
        st.session_state.restaurant_name = st.sidebar.text_input("உணவகப் பெயர்:", value=st.session_state.restaurant_name)
        st.session_state.restaurant_address = st.sidebar.text_area("முகவரி (Address):", value=st.session_state.restaurant_address)
        st.session_state.restaurant_phone = st.sidebar.text_input("தொலைபேசி எண்:", value=st.session_state.restaurant_phone)
        st.sidebar.success("கடை விபரங்கள் புதுப்பிக்கப்பட்டன!")

    # 2. Edit Menu Item
    elif admin_action == "உணவு விலை/படம் மாற்று":
        if st.session_state.menu_data:
            selected_edit_id = st.sidebar.selectbox(
                "உணவை தேர்வு செய்யவும்:", 
                list(st.session_state.menu_data.keys()), 
                format_func=lambda x: st.session_state.menu_data[x]["item"]
            )
            new_price = st.sidebar.number_input(
                f"{st.session_state.menu_data[selected_edit_id]['item']} புதிய விலை:", 
                min_value=0.0, value=float(st.session_state.menu_data[selected_edit_id]['price']), step=5.0
            )
            st.session_state.menu_data[selected_edit_id]['price'] = new_price

            uploaded_file = st.sidebar.file_uploader("புகைப்படம் பதிவேற்றவும்:", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                st.session_state.menu_data[selected_edit_id]['image'] = Image.open(uploaded_file)
                st.sidebar.success("புகைப்படம் மாற்றப்பட்டது!")

    # 3. Add Item
    elif admin_action == "புதிய உணவு சேர் (Add)":
        st.sidebar.write("### ➕ புதிய உணவு விவரம்:")
        new_item_name = st.sidebar.text_input("உணவின் பெயர் (Item Name):")
        new_item_price = st.sidebar.number_input("விலை (Price):", min_value=0.0, step=5.0)
        new_item_file = st.sidebar.file_uploader("உணவு புகைப்படம் (Optional):", type=["jpg", "jpeg", "png"], key="add_img")
        
        if st.sidebar.button("பட்டியலில் சேர் (Add Item)"):
            if new_item_name:
                new_id = max(st.session_state.menu_data.keys()) + 1 if st.session_state.menu_data else 1
                new_img = Image.open(new_item_file) if new_item_file is not None else None
                
                st.session_state.menu_data[new_id] = {
                    "item": new_item_name,
                    "price": new_item_price,
                    "image": new_img
                }
                st.sidebar.success(f"🎉 {new_item_name} வெற்றிகரமாக சேர்க்கப்பட்டது!")
                st.rerun()

    # 4. Remove Item
    elif admin_action == "உணவை நீக்கு (Remove)":
        if st.session_state.menu_data:
            selected_delete_id = st.sidebar.selectbox(
                "நீக்க வேண்டிய உணவு:", 
                list(st.session_state.menu_data.keys()), 
                format_func=lambda x: st.session_state.menu_data[x]["item"]
            )
            item_to_remove = st.session_state.menu_data[selected_delete_id]['item']
            if st.sidebar.button(f"🗑️ {item_to_remove}-ஐ நீக்கு", type="primary"):
                del st.session_state.menu_data[selected_delete_id]
                st.sidebar.success(f"🗑️ {item_to_remove} நீக்கப்பட்டது!")
                st.rerun()
else:
    if admin_password_input != "":
        st.sidebar.error("🔒 தவறான கடவுச்சொல்!")
    else:
        st.sidebar.info("🔑 மேலாளர் பகுதிக்கு கடவுச்சொல்லை உள்ளிடவும்.")


# --- TAB 1: ORDERING & BILLING SCREEN ---
with tab1:
    st.markdown(f"<h1 style='text-align: center; color: #2E4053;'>📱 {st.session_state.restaurant_name}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 10pt; color: #7F8C8D;'>{st.session_state.restaurant_address} | 📞 {st.session_state.restaurant_phone}</p>", unsafe_allow_html=True)
    st.write("---")
    
    st.write("### 🍽️ இன்றைய உணவுப் பட்டியல்")
    order_cart = {}

    if st.session_state.menu_data:
        for code, details in st.session_state.menu_data.items():
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    if details["image"] is not None:
                        st.image(details["image"], use_column_width=True)
                    else:
                        st.write("📷 படம் இல்லை")
                with col2:
                    st.markdown(f"*{details['item']}*")
                    st.write(f"விலை: ரூ. {details['price']}")
                    qty = st.number_input("அளவு (Quantity)", min_value=0, step=1, key=f"qty_{code}")
                    if qty > 0:
                        order_cart[code] = qty
            st.markdown("---")

    # Generate Bill Layout
    if order_cart:
        # Generate temporary Bill ID and Date
        bill_id = random.randint(1000, 9999)
        current_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        
        # Receipt UI Block
        st.markdown("<div style='border: 2px dashed #BDC3C7; padding: 15px; border-radius: 5px; background-color: #FAFAFA;'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; margin: 0;'>{st.session_state.restaurant_name}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 9pt; margin: 2px;'>{st.session_state.restaurant_address}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 9pt; margin: 2px;'>📞 Cell: {st.session_state.restaurant_phone}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        st.markdown(f"<p style='font-size: 10pt;'><b>பில் எண்:</b> #{bill_id} <span style='float: right;'><b>தேதி:</b> {current_time}</span></p>", unsafe_allow_html=True)
        
        bill_items = []
        grand_total = 0.0
        
        for code, qty in order_cart.items():
            name = st.session_state.menu_data[code]["item"]
            u_price = st.session_state.menu_data[code]["price"]
            tot_price = qty * u_price
            grand_total += tot_price
            bill_items.append({"உணவு": name, "அளவு": qty, "விலை (ரூ)": u_price, "மொத்தம் (ரூ)": tot_price})
        
        df = pd.DataFrame(bill_items)
        st.table(df)
        
        st.markdown(f"<h3 style='text-align: right; color: #27AE60; margin-top: 5px;'>மொத்த தொகை: ரூ. {grand_total}</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 10pt; font-style: italic;'>மீண்டும் வருக! Thank you!</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")
        
        if st.button("பில் செய்ய உறுதிசெய்", type="primary"):
            now_save = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_history_data = []
            for code, qty in order_cart.items():
                new_history_data.append({
                    "பில் எண்": f"#{bill_id}",
                    "தேதி / நேரம்": now_save,
                    "உணவு": st.session_state.menu_data[code]["item"],
                    "அளவு": qty,
                    "விலை": st.session_state.menu_data[code]["price"],
                    "மொத்த தொகை": qty * st.session_state.menu_data[code]["price"]
                })
            
            new_df = pd.DataFrame(new_history_data)
            if os.path.exists(HISTORY_FILE):
                old_df = pd.read_csv(HISTORY_FILE)
                combined_df = pd.concat([old_df, new_df], ignore_index=True)
                combined_df.to_csv(HISTORY_FILE, index=False)
            else:
                new_df.to_csv(HISTORY_FILE, index=False)
                
            st.balloons()
            st.success("🎉 பில் வரலாற்றில் வெற்றிகரமாகச் சேமிக்கப்பட்டது!")
    else:
        st.info("💡 ஆர்டர் செய்ய உணவின் அளவை (Quantity) உள்ளிடவும்.")


# --- TAB 2: SALES HISTORY (Admin Only) ---
with tab2:
    st.write("### 📊 மொத்த விற்பனை வரலாறு (Total Sales History)")
    
    if admin_password_input == ADMIN_PASSWORD:
        if os.path.exists(HISTORY_FILE):
            history_df = pd.read_csv(HISTORY_FILE)
            st.dataframe(history_df, use_container_width=True)
            
            total_sales = history_df["மொத்த தொகை"].sum()
            st.markdown(f"<h2 style='text-align: center; color: #E74C3C;'>இதுவரையிலான மொத்த விற்பனை: ரூ. {total_sales}</h2>", unsafe_allow_html=True)
            
            if st.button("வரலாற்றை அழிக்கவும் (Clear History)"):
                os.remove(HISTORY_FILE)
                st.rerun()
        else:
            st.info("📂 இதுவரை எந்த விற்பனை வரலாறும் இல்லை.")
    else:
        st.warning("🔒 இந்த விபரங்களை பார்க்க உங்களுக்கு அனுமதி இல்லை! மேலாளர் கடவுச்சொல்லை உள்ளிடவும்.")
