import streamlit as st
from PIL import Image
import pandas as pd
import datetime
import os

st.set_page_config(page_title="Mobile Restaurant App", page_icon="🍔", layout="centered")

# Excel History File Setup
HISTORY_FILE = "sales_history.csv"

# Initialize Session State for Menu Items
if 'menu_data' not in st.session_state:
    st.session_state.menu_data = {
        1: {"item": "Plain Dosa", "price": 50.0, "image": None},
        2: {"item": "Masala Dosa", "price": 70.0, "image": None},
        3: {"item": "Idli (2 Pcs)", "price": 30.0, "image": None},
        4: {"item": "Vada (1 Pc)", "price": 20.0, "image": None},
        5: {"item": "Coffee", "price": 25.0, "image": None},
        6: {"item": "Tea", "price": 20.0, "image": None}
    }

# Tab Navigation: Orders and History separation
tab1, tab2 = st.tabs(["🍽️ இன்றைய ஆர்டர்", "📊 விற்பனை வரலாறு (History)"])

with tab1:
    # Admin Sidebar Section
    st.sidebar.markdown("<h2 style='color: #E67E22;'>🛠️ மேலாளர் பகுதி (Admin)</h2>", unsafe_allow_html=True)
    st.sidebar.write("விலை மற்றும் புகைப்படங்களை இங்கே மாற்றவும்:")

    selected_edit_id = st.sidebar.selectbox(
        "உணவை தேர்வு செய்யவும்:", 
        list(st.session_state.menu_data.keys()), 
        format_func=lambda x: st.session_state.menu_data[x]["item"]
    )

    new_price = st.sidebar.number_input(
        f"{st.session_state.menu_data[selected_edit_id]['item']} புதிய விலை:", 
        min_value=0.0, 
        value=float(st.session_state.menu_data[selected_edit_id]['price']), 
        step=5.0
    )
    st.session_state.menu_data[selected_edit_id]['price'] = new_price

    uploaded_file = st.sidebar.file_uploader(
        f"{st.session_state.menu_data[selected_edit_id]['item']} புகைப்படம் பதிவேற்றவும்:", 
        type=["jpg", "jpeg", "png"]
    )
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.session_state.menu_data[selected_edit_id]['image'] = img
        st.sidebar.success("புகைப்படம் வெற்றிகரமாக மாற்றப்பட்டது!")

    st.markdown("<h1 style='text-align: center; color: #2E4053;'>📱 உணவகப் பட்டியல் & பில்</h1>", unsafe_allow_html=True)
    st.write("### 🍽️ இன்றைய உணவுப் பட்டியல்")
    order_cart = {}

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
            # Save to Excel History
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

with tab2:
    st.write("### 📊 மொத்த விற்பனை வரலாறு (Total Sales History)")
    if os.path.exists(HISTORY_FILE):
        history_df = pd.read_csv(HISTORY_FILE)
        
        # Display the entire history table
        st.dataframe(history_df, use_container_width=True)
        
        # Calculate and Display overall grand total sum
        total_sales = history_df["மொத்த தொகை"].sum()
        st.markdown(f"<h2 style='text-align: center; color: #E74C3C;'>இதுவரையிலான மொத்த விற்பனை: ரூ. {total_sales}</h2>", unsafe_allow_html=True)
        
        # Option to clear history if needed
        if st.button("வரலாற்றை அழிக்கவும் (Clear History)"):
            os.remove(HISTORY_FILE)
            st.experimental_rerun()
    else:
        st.info("📂 இதுவரை எந்த விற்பனை வரலாறும் இல்லை.")
