
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from bsutennis import TennisCourt

def test_advanced():
    # Generate realistic shot landing points (in standard vertical coordinates)
    # Player's shot landing points (opponent's side, 0 to 11.89)
    np.random.seed(42)
    player_shots_x = np.random.normal(0, 2.5, 15)  # Width spread
    player_shots_y = np.random.uniform(3, 11, 15)  # Depth (service line to baseline)
    
    # Opponent's return landing points (player's side, -11.89 to 0)
    opponent_returns_x = np.random.normal(0, 2.8, 15)
    opponent_returns_y = np.random.uniform(-11, -2, 15)
    
    # 1. Scatter (Horizontal)
    print("Testing Scatter (Horizontal)...")
    court = TennisCourt(orientation='horizontal', theme='bsu')
    fig, ax = plt.subplots(figsize=(10, 6))
    court.draw(ax=ax)
    court.scatter(ax, player_shots_x, player_shots_y, color='#e74c3c', s=60, 
                  edgecolors='black', linewidths=0.5, alpha=0.8, label='Shot Landing Points')
    court.scatter(ax, opponent_returns_x, opponent_returns_y, color='#3498db', s=60,
                  edgecolors='black', linewidths=0.5, alpha=0.8, label='Opponent Return Landing Points')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 0), ncol=2, frameon=True, fancybox=True)
    plt.title("Shot Landing Analysis (Horizontal)", fontsize=12, pad=10)
    plt.savefig("test_scatter_h.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # 2. Scatter (Vertical)
    print("Testing Scatter (Vertical)...")
    court_v = TennisCourt(orientation='vertical', theme='bsu')
    fig, ax = plt.subplots(figsize=(6, 10))
    court_v.draw(ax=ax)
    court_v.scatter(ax, player_shots_x, player_shots_y, color='#e74c3c', s=60,
                    edgecolors='black', linewidths=0.5, alpha=0.8, label='Shot Landing Points')
    court_v.scatter(ax, opponent_returns_x, opponent_returns_y, color='#3498db', s=60,
                    edgecolors='black', linewidths=0.5, alpha=0.8, label='Opponent Return Landing Points')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 0.05), ncol=1, frameon=True, fancybox=True, fontsize=9)
    plt.title("Shot Landing Analysis (Vertical)", fontsize=12)
    plt.savefig("test_scatter_v.png", dpi=150, bbox_inches='tight')
    
    # 3. KDE (Vertical)
    print("Testing KDE (Vertical)...")
    fig, ax = plt.subplots(figsize=(6, 10))
    court_v.draw(ax=ax)
    court_v.kdeplot(ax, player_shots_x, player_shots_y, cmap='Reds', alpha=0.4,
                  clip=([court.x_min, court.x_max], [court.y_min, court.y_max]))
    plt.title("Shot Density (KDE)", fontsize=12, pad=10)
    plt.savefig("test_kde_v.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # 4. Arrows
    print("Testing Arrows...")
    # Shot from baseline to service line
    x_start = [0, 0]
    y_start = [5, 6]
    x_end = [15, 16]
    y_end = [3, 8]
    
    court_h = TennisCourt(orientation='horizontal', theme='bsu')
    fig, ax = plt.subplots(figsize=(10, 6))
    court_h.draw(ax=ax)
    court_h.arrows(ax, x_start, y_start, x_end, y_end, color='black') # black arrows on white
    plt.title("Arrows Horizontal (BSU Theme)")
    plt.savefig("test_arrows_h.png")
    plt.close()

if __name__ == "__main__":
    try:
        test_advanced()
        print("Advanced tests passed!")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
