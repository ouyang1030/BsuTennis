
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from bsutennis import TennisCourt

def test_scatter_styles():
    print("Testing Scatter Styles...")
    
    court = TennisCourt(orientation='vertical', half=True, theme='bsu')
    fig, ax = plt.subplots(figsize=(6, 8))
    court.draw(ax=ax)
    
    # Simulate different event types
    
    # 1. FH Winner (Red Star)
    court.scatter(ax, [2, 3], [8, 9], style='winner_fh', label='FH Winner')
    
    # 2. BH Winner (Blue Star)
    court.scatter(ax, [-2, -3], [8, 9], style='winner_bh', label='BH Winner')
    
    # 3. UE (Triangle Error)
    court.scatter(ax, [0, 0.5], [5, 4], style='ue', label='Unforced Error')
    
    # 4. Ace (Star Error color)
    court.scatter(ax, [3, -3], [1, 1], style='ace', label='Ace')
    
    # 5. Generic (Dots)
    court.scatter(ax, [1, -1], [7, 7], style='landing', label='Landing')

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, frameon=False)
    plt.title("Scatter Styles")
    plt.savefig("test_scatter_styles.png")
    plt.close()

if __name__ == "__main__":
    try:
        test_scatter_styles()
        print("Scatter Style tests passed!")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
