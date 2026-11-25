
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from bsutennis import TennisCourt

def test_combo_plot():
    print("Testing Combo Plots (KDE + Scatter)...")
    
    # Court boundaries for half court (vertical)
    # x: -4.115 to 4.115 (singles width)
    # y: 0 to 11.89 (half length)
    
    # 1. Generate Rally Data (for KDE)
    # Clusters mainly deep in corners and center
    x_rally = np.concatenate([
        np.random.normal(3, 1, 300), 
        np.random.normal(-3, 1, 300),
        np.random.normal(0, 1.5, 200)
    ])
    x_rally = np.clip(x_rally, -4.115, 4.115)  # Clip to court width
    
    y_rally = np.random.normal(10, 2.5, 800)
    y_rally = np.clip(y_rally, 0, 11.89)  # Clip to court length

    # 2. Generate Event Data (for Scatter)
    # Winners near lines
    x_win_fh = np.random.normal(3.5, 0.5, 20)
    x_win_fh = np.clip(x_win_fh, -4.115, 4.115)
    y_win_fh = np.random.normal(9, 2, 20)
    y_win_fh = np.clip(y_win_fh, 0, 11.89)
    
    x_win_bh = np.random.normal(-3.5, 0.5, 20)
    x_win_bh = np.clip(x_win_bh, -4.115, 4.115)
    y_win_bh = np.random.normal(9, 2, 20)
    y_win_bh = np.clip(y_win_bh, 0, 11.89)
    
    # Errors near net
    x_err = np.random.uniform(-4, 4, 30)
    x_err = np.clip(x_err, -4.115, 4.115)
    y_err = np.random.normal(6.4, 1, 30)
    y_err = np.clip(y_err, 0, 11.89)

    # Plot Combo
    court = TennisCourt(half=True, theme='bsu')
    fig, ax = plt.subplots(figsize=(6, 8))
    court.draw(ax=ax)
    
    # A. Draw KDE Background (All Shots) with clipping
    court.kdeplot(ax, x_rally, y_rally, cmap='bsu_green', levels=50, alpha=0.4,
                  clip=([court.x_min, court.x_max], [court.y_min, court.y_max]))
    
    # B. Overlay Events
    court.scatter(ax, x_win_fh, y_win_fh, style='winner_fh', label='FH Winner')
    court.scatter(ax, x_win_bh, y_win_bh, style='winner_bh', label='BH Winner')
    court.scatter(ax, x_err, y_err, style='ue', label='Unforced Error')
    
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.02), ncol=3, frameon=False)
    plt.title("Shot Distribution & Key Events")
    
    plt.savefig("test_combo.png")
    plt.close()

if __name__ == "__main__":
    try:
        test_combo_plot()
        print("Combo tests passed!")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
