
import pandas as pd
from app.core.processor import Processor

def test_logic():
    # Test cases derived from logic inspection
    # 2026-01-01 is a Thursday
    
    dates = [
        pd.Timestamp("2026-01-01"), # Thu (4) -> +2 extra days
        pd.Timestamp("2026-01-02"), # Fri (5) -> +2 extra days
        pd.Timestamp("2026-01-03"), # Sat (6) -> +1 extra day
        pd.Timestamp("2026-01-04"), # Sun (7) -> +0 extra day
        pd.Timestamp("2026-01-05"), # Mon (1) -> +0 extra day
    ]
    
    # Test CN (2 days normally)
    print("Testing CN (2 days base)...")
    base_days = 2
    
    for d in dates:
        row = {'Conclusão desejada': d, 'Acréscimo de dias': base_days}
        res = Processor.calculate_real_deadline(row)
        diff = (res - d).days
        weekday = d.weekday() + 1
        print(f"Date: {d.date()} (Day {weekday}) | Result: {res.date()} | Diff: {diff}")

    # Test CT (0 days)
    print("\nTesting CT (0 days)...")
    for d in dates:
        row = {'Conclusão desejada': d, 'Acréscimo de dias': 0}
        res = Processor.calculate_real_deadline(row)
        print(f"Date: {d.date()} | Result: {res}")

if __name__ == "__main__":
    test_logic()
