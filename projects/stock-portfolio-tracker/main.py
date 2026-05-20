import time
from src.portfolio.trades import buy_stock, sell_stock, view_trades

def seed_test_data():
    print("Initializing test trade data injection...\n")
    
    # ---------------------------------------------------------
    # 1. Simulate Apple (AAPL) Trades
    # ---------------------------------------------------------
    print("Executing AAPL orders...")
    # Initial position
    buy_stock(ticker="AAPL", quantity=10, price=175.50)
    time.sleep(0.5) # Small pause to keep transaction logs distinct if needed
    
    # Adding to the position
    buy_stock(ticker="AAPL", quantity=5, price=180.25)
    time.sleep(0.5)
    
    # Taking partial profits
    sell_stock(ticker="AAPL", quantity=3, price=190.00)
    print("AAPL history updated.")
    
    # ---------------------------------------------------------
    # 2. Simulate NVIDIA (NVDA) Trades
    # ---------------------------------------------------------
    print("\nExecuting NVDA orders...")
    # Initial position
    buy_stock(ticker="NVDA", quantity=20, price=450.00)
    time.sleep(0.5)
    
    # Adding to the position
    buy_stock(ticker="NVDA", quantity=10, price=480.50)
    time.sleep(0.5)
    
    # Taking partial profits
    sell_stock(ticker="NVDA", quantity=5, price=520.00)
    print("NVDA history updated.")
    
    # ---------------------------------------------------------
    # 3. Verify Transactions in Console
    # ---------------------------------------------------------
    print("\n--- Current Transaction Log (Database View) ---")
    df_trades = view_trades()
    if df_trades is not None and not df_trades.empty:
        print(df_trades)
    else:
        print("Trades were executed but could not be parsed into a DataFrame.")
        
    print("\nSeed data complete! Run your Streamlit app to view the live dashboard.")

if __name__ == "__main__":
    seed_test_data()