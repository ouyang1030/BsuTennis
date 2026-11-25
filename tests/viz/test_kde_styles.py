
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from bsutennis import TennisCourt

def test_kde_styles():
    print("Testing KDE Styles...")
    
    # Generate realistic shot data (forehand and backhand)
    np.random.seed(42)
    
    # Forehand shots (right side, positive x)
    fh_x = np.random.normal(2.5, 1.5, 25)
    fh_y = np.random.uniform(2, 10, 25)
    
    # Backhand shots (left side, negative x)
    bh_x = np.random.normal(-2.5, 1.5, 25)
    bh_y = np.random.uniform(2, 10, 25)
    
    # 1. Green KDE 
    print("Testing Green KDE...")
    court = TennisCourt(half=True, theme='bsu')
    fig, ax = plt.subplots(figsize=(6, 8))
    court.draw(ax=ax)
    
    # Combine all shots
    all_x = np.concatenate([fh_x, bh_x])
    all_y = np.concatenate([fh_y, bh_y])
    
    # KDE with clipping to court boundaries
    court.kdeplot(ax, all_x, all_y, cmap='bsu_green', levels=50, alpha=0.4,
                  clip=([court.x_min, court.x_max], [court.y_min, court.y_max]))
    
    # Overlay scatter points as stars
    court.scatter(ax, all_x, all_y, marker='*', s=80, color='#92e3da', 
                  edgecolors='black', linewidths=0.5, alpha=0.6)
    
    plt.title("Shot Density (Green)", fontsize=12, pad=10)
    plt.savefig("test_kde_green.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # 2. Red KDE (Forehand)
    print("Testing Red KDE...")
    court = TennisCourt(half=True, theme='bsu')
    fig, ax = plt.subplots(figsize=(6, 8))
    court.draw(ax=ax)
    
    # KDE with clipping
    court.kdeplot(ax, fh_x, fh_y, cmap='bsu_red', levels=50, alpha=0.4,
                  clip=([court.x_min, court.x_max], [court.y_min, court.y_max]))
    
    # Overlay forehand shots as red stars
    court.scatter(ax, fh_x, fh_y, marker='*', s=80, color='#ff3b3b',
                  edgecolors='black', linewidths=0.5, alpha=0.6)
    
    plt.title("Forehand Shot Density", fontsize=12, pad=10)
    plt.savefig("test_kde_red.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # 3. Blue KDE
    print("Testing Blue KDE...")
    court = TennisCourt(half=True, theme='bsu')
    fig, ax = plt.subplots(figsize=(6, 8))
    court.draw(ax=ax)
    
    # KDE with clipping
    court.kdeplot(ax, bh_x, bh_y, cmap='bsu_blue', levels=50, alpha=0.4,
                  clip=([court.x_min, court.x_max], [court.y_min, court.y_max]))
    
    # Overlay backhand shots as blue stars
    court.scatter(ax, bh_x, bh_y, marker='*', s=80, color='#2437ff',
                  edgecolors='black', linewidths=0.5, alpha=0.6)
    
    plt.title("Backhand Shot Density", fontsize=12, pad=10)
    plt.savefig("test_kde_blue.png", dpi=150, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    try:
        test_kde_styles()
        print("KDE style tests passed!")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
