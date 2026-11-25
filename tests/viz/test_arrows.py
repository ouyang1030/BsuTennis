
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from bsutennis import TennisCourt
from matplotlib.lines import Line2D

def test_arrows():
    print("Testing Enhanced Arrows...")
    
    # Create court
    court = TennisCourt(theme='bsu')
    fig, ax = plt.subplots(figsize=(12, 7))
    court.draw(ax=ax)
    
    # 1. Solid arrows 
    # Baseline to deep corner
    court.arrows(ax, 
                x_start=[-3, -2], 
                y_start=[-10, -9], 
                x_end=[3.5, 3], 
                y_end=[10, 9.5],
                color='#e74c3c', 
                linewidth=3,
                linestyle='solid',
                arrow_style='fancy',
                alpha=0.9)
    
    # 2. Dashed arrows 
    court.arrows(ax,
                x_start=[3, 2.5],
                y_start=[-10, -9.5],
                x_end=[-3.5, -3],
                y_end=[10.5, 10],
                color='#3498db',
                linewidth=2.5,
                linestyle='dashed',
                arrow_style='fancy',
                alpha=0.8)
    
    # 3. Dotted arrows for anticipated movement
    court.arrows(ax,
                x_start=[0, 0],
                y_start=[-8, -6],
                x_end=[2, -2],
                y_end=[8, 8],
                color='#95a5a6',
                linewidth=2,
                linestyle='dotted',
                arrow_style='simple',
                alpha=0.6)
    
    # 4. Simple arrows for serve trajectories
    court.arrows(ax,
                x_start=[0, 0],
                y_start=[-11.5, -11.5],
                x_end=[3, -3],
                y_end=[6, 6],
                color='#2ecc71',
                linewidth=2.5,
                linestyle='solid',
                arrow_style='curve',
                alpha=0.85)
    
    # Add legend
    legend_elements = [
        Line2D([0], [0], color='#e74c3c', linewidth=3, linestyle='-', 
               label='Forehand Shot', marker='>', markersize=8),
        Line2D([0], [0], color='#3498db', linewidth=2.5, linestyle='--', 
               label='Backhand Shot', marker='>', markersize=8),
        Line2D([0], [0], color='#95a5a6', linewidth=2, linestyle=':', 
               label='Movement', marker='>', markersize=8),
        Line2D([0], [0], color='#2ecc71', linewidth=2.5, linestyle='-', 
               label='Serve', marker='>', markersize=8),
    ]
    plt.legend(handles=legend_elements, loc='upper center', 
              bbox_to_anchor=(0.5, -0.03), ncol=4, frameon=True, fancybox=True)
    
    plt.title("Shot Trajectories & Movement Paths", fontsize=14, pad=15, weight='bold')
    plt.savefig("test_arrows_h.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Arrow tests passed!")

if __name__ == "__main__":
    try:
        test_arrows()
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
