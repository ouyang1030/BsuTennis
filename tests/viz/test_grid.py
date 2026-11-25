
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from bsutennis import create_court_grid

def test_court_grids():
    # Test 1: 1 row × 3 columns (Vertical Half Courts)
    print("Testing 1×3 Grid (Vertical)...")
    fig, axes, courts = create_court_grid(nrows=1, ncols=3, orientation='vertical', half=True)
    
    # Draw courts with different guide configurations
    for i, (ax, court) in enumerate(zip(axes.flat, courts)):
        court.draw(ax=ax)
        if i == 0:
            court.draw_guides(ax, service_vertical_lines=1, backcourt_line=False)
            ax.set_title("Bisect Service")
        elif i == 1:
            court.draw_guides(ax, service_vertical_lines=2, backcourt_line=False)
            ax.set_title("Trisect Service")
        else:
            court.draw_guides(ax, service_vertical_lines=2, backcourt_line=True)
            ax.set_title("Service + Backcourt")
    
    plt.suptitle("1×3 Grid: Vertical Half Courts", fontsize=14, y=0.98)
    plt.savefig("test_grid_1x3_vertical.png", dpi=100, bbox_inches='tight')
    plt.close()
    
    # Test 2: 2 rows × 3 columns (Horizontal Half Courts)
    print("Testing 2×3 Grid (Horizontal)...")
    fig, axes, courts = create_court_grid(nrows=2, ncols=3, orientation='horizontal', half=True)
    
    players = ["Player A", "Player B", "Player C", "Player D", "Player E", "Player F"]
    for i, (ax, court) in enumerate(zip(axes.flat, courts)):
        court.draw(ax=ax)
        # Alternate guide styles
        if i % 2 == 0:
            court.draw_guides(ax, service_vertical_lines=2, backcourt_line=False)
        else:
            court.draw_guides(ax, service_vertical_lines=1, backcourt_line=True)
        ax.set_title(players[i], fontsize=10, pad=5)
    
    plt.suptitle("2×3 Grid: Player Comparison", fontsize=14, y=0.99)
    plt.savefig("test_grid_2x3_horizontal.png", dpi=100, bbox_inches='tight')
    plt.close()
    
    # Test 3: 3 rows × 3 columns (Compact Grid)
    print("Testing 3×3 Grid (Vertical)...")
    fig, axes, courts = create_court_grid(nrows=3, ncols=3, orientation='vertical', half=True, figsize=(12, 14))
    
    for i, (ax, court) in enumerate(zip(axes.flat, courts)):
        court.draw(ax=ax)
        court.draw_guides(ax, service_vertical_lines=2, backcourt_line=True)
        ax.set_title(f"Match {i+1}", fontsize=9, pad=3)
    
    plt.suptitle("3×3 Grid: Multi-Match Analysis", fontsize=14, y=0.995)
    plt.savefig("test_grid_3x3_vertical.png", dpi=100, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    try:
        test_court_grids()
        print("Grid tests passed!")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
