# Restaurant Menu Card
MENU = {
    1: {"item": "Plain Dosa", "price": 50},
    2: {"item": "Masala Dosa", "price": 70},
    3: {"item": "Idli (2 Pcs)", "price": 30},
    4: {"item": "Vada (1 Pc)", "price": 20},
    5: {"item": "Coffee", "price": 25},
    6: {"item": "Tea", "price": 20}
}

def display_menu():
    print("\n" + "="*30)
    print("      RESTAURANT MENU")
    print("="*30)
    for code, details in MENU.items():
        print(f"{code}. {details['item']:<15} - Rs.{details['price']}")
    print("="*30)

def generate_bill():
    order = {}
    display_menu()
    
    while True:
        try:
            choice = int(input("\nItem Code-a enter pannunga (Stop panna '0' thavunga): "))
            if choice == 0:
                break
            if choice not in MENU:
                print("Thappan code! Please select a valid item.")
                continue
                
            quantity = int(input(f"{MENU[choice]['item']} evlo venum (Quantity)? "))
            if quantity <= 0:
                print("Quantity 1-vathu irukka vendum.")
                continue
                
            # Add or update order
            if choice in order:
                order[choice] += quantity
            else:
                order[choice] = quantity
        except ValueError:
            print("Dayavu seidhu number-a enter pannunga!")

    if not order:
        print("\nOrder ethuvum edukkapadavillai.")
        return

    # Print Bill Receipt
    print("\n" + "*"*35)
    print("          FINAL BILL")
    print("*"*35)
    print(f"{'Item':<15} {'Qty':<5} {'Price':<8} {'Total':<5}")
    print("-"*35)
    
    grand_total = 0
    for code, qty in order.items():
        item_name = MENU[code]["item"]
        price = MENU[code]["price"]
        total_price = qty * price
        grand_total += total_price
        print(f"{item_name:<15} {qty:<5} Rs.{price:<6} Rs.{total_price}")
        
    print("-"*35)
    print(f"Grand Total:           Rs.{grand_total}")
    print("*"*35)
    print("Thank you! Visit Again.")

# Run the software
if __name__ == "__main__":
    generate_bill()
