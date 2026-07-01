import streamlit as st
from PIL import Image
import pandas as pd
import datetime
import os

st.set_page_config(page_title="Mobile Restaurant App", page_icon="🍔", layout="centered")

HISTORY_FILE = "sales_history.csv"

# 1. Load / Initialize Menu Data permanently using Session State
if 'menu_data' not in st.session_state:
    st.session_state.menu_data = {
        1: {"item": "Plain Dosa", "price": 50.0, "image": None},
        2: {"item": "Masala Dosa", "price": 70.0, "image": None},
        3: {"item": "Idli (2 Pcs)", "price": 30.0, "image": None},
        4: {"item": "Vada (1 Pc)", "price": 20.0, "image": None}
    }

# Tab Layout Separation
tab1, tab2 = st.tabs(["🍽️ இன்றைய ஆர்டர்", "📊 விற்பனை வரலாறு (History)"])

# --- ADMIN SIDEBAR EDITOR ---
st.sidebar.markdown("<h2 style='color: #E67E22;'>🛠️ மேலாளர் பகுதி (Admin)</h2>", unsafe_allow_html=True)

# Admin Sub-Options: Edit, Add, or Remove
admin_action = st.sidebar.radio("என்ன செய்ய வேண்டும்?", ["விலை/படம் மாற்று", "புதிய உணவு சேர் (Add)", "உணவை நீக்கு (Remove)"])

if admin_action == "விலை/படம் மாற்று":
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
    else:
        st.sidebar.info("பட்டியல் காலியாக உள்ளது.")

elif admin_action == "புதிய உணவு சேர் (Add)":
    st.sidebar.write("### ➕ புதிய உணவு விவரம்:")
    new_item_name = st.sidebar.text_input("உணவின் பெயர் (Item Name):")
    new_item_price = st.sidebar.number_input("விலை (Price):", min_value=0.0, step=5.0)
    new_item_file = st.sidebar.file_uploader("உணவு புகைப்படம் (Optional):", type=["jpg", "jpeg", "png"], key="add_img")
    
    if st.sidebar.button("பட்டியலில் சேர் (Add Item)"):
        if new_item_name:
            # Generate a new unique ID
            new_id = max(st.session_state.menu_data.keys()) + 1 if st.session_state.menu_data else 1
            new_img = Image.open(new_item_file) if new_item_file is not None else None
            
            st.session_state.menu_data[new_id] = {
                "item": new_item_name,
                "price": new_item_price,
                "image": new_img
            }
            st.sidebar.success(f"🎉 {new_item_name} வெற்றிகரமாக சேர்க்கப்பட்டது!")
            st.rerun()
        else:
            st.sidebar.error("தயவுசெய்து உணவின் பெயரை டைப் செய்யவும்!")

elif admin_action == "உணவை நீக்கு (Remove)":
    st.sidebar.write("### ❌ உணவை நீக்குதல்:")
    if st.session_state.menu_data:
        selected_delete_id = st.sidebar.selectbox(
            "நீக்க வேண்டிய உணவு:", 
            list(st.session_state.menu_data.keys()), 
            format_func=lambda x: st.session_state.menu_data[x]["item"],
            key="delete_box"
        )
        item_to_remove = st.session_state.menu_data[selected_delete_id]['item']
        
        if st.sidebar.button(f"🗑️ {item_to_remove}-ஐ நீக்கு", type="primary"):
            del st.session_state.menu_data[selected_delete_id]
            st.sidebar.success(f"🗑️ {item_to_remove} பட்டியலிலிருந்து நீக்கப்பட்டது!")
            st.rerun()
    else:
        st.sidebar.info("நீக்குவதற்கு உணவுகள் எதுவும் இல்லை.")


# --- TAB 1: ORDERING SCREEN ---
with tab1:
    st.markdown("<h1 style='text-align: center; color: #2E4053;'>📱 உணவகப் பட்டியல் & பில்</h1>", unsafe_allow_html=True)
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
    else:
        st.warning("⚠️ உணவுப் பட்டியல் காலியாக உள்ளது! Admin பகுதியில் உணவுகளை சேர்க்கவும்.")

    # Billing System
    if order_cart:
        st.write("### 🧾 உங்களுடைய பில் விபரம்")
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
        
        st.markdown(f"<h3 style='text-align: right; color: #27AE60;'>மொத்த தொகை: ரூ. {grand_total}</h3>", unsafe_allow_html=True)
        
        if st.button("பில் செய்ய உறுதிசெய்", type="primary"):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_history_data = []
            for code, qty in order_cart.items():
                new_history_data.append({
                    "தேதி / நேரம்": now,
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
            st.success("🎉 பில் வெற்றிகரமாக உருவாக்கப்பட்டு, வரலாற்றில் சேமிக்கப்பட்டது!")
    else:
        st.info("💡 ஆர்டர் செய்ய உணவின் அளவை (Quantity) உள்ளிடவும்.")


# --- TAB 2: SALES HISTORY ---
with tab2:
    st.write("### 📊 மொத்த விற்பனை வரலாறு (Total Sales History)")
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
