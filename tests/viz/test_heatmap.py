
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from bsutennis import TennisCourt

def test_heatmap():
    print("Testing Heatmap (Grid)...")
    
    # Generate mock data over the whole court
    x = np.random.normal(0, 3, 500)
    y = np.random.uniform(0, 23, 500)
    
    # 1. Standard Count Heatmap (5x5 bins)
    court = TennisCourt(orientation='vertical', half=False, theme='bsu')
    fig, ax = plt.subplots(figsize=(6, 10))
    court.draw(ax=ax)
    court.heatmap(ax, x, y, bins=[5, 8], statistic='count', cmap='Blues', annot=True, alpha=0.7)
    plt.title("Grid Heatmap (Counts)")
    plt.savefig("test_heatmap_counts.png")
    plt.close()
    
    # 2. Frequency Heatmap (Percentages) - Half Court
    court = TennisCourt(orientation='vertical', half=True, theme='bsu')
    fig, ax = plt.subplots(figsize=(8, 8))
    court.draw(ax=ax)
    # Use 'half=True' to automatically clip data to half court
    # Use 'gridsize' instead of 'bins' to test alias
    court.heatmap(ax, x, y, gridsize=4, statistic='frequency', cmap='Reds', annot=True, fmt='.1f', 
                  half=True, alpha=0.7, edgecolor='white', linewidth=1)
    plt.title("Grid Heatmap (Frequency %)")
    plt.savefig("test_heatmap_freq.png")
    plt.close()

    # 3. Hexbin Plot - Full Court
    court = TennisCourt(orientation='vertical', half=False, theme='bsu')
    fig, ax = plt.subplots(figsize=(6, 10))
    court.draw(ax=ax)
    # 'half=False' ensures full court extent
    court.hexbin(ax, x, y, gridsize=20, cmap='bsu_green', mincnt=1, 
                 half=False, edgecolors='white', linewidths=0.5)
    plt.title("Hexbin Plot (Full)")
    plt.savefig("test_heatmap_hex.png")
    plt.close()

    # 4. Hexbin Plot - Half Court (Clipped)
    court = TennisCourt(orientation='vertical', half=True, theme='bsu')
    fig, ax = plt.subplots(figsize=(8, 8))
    court.draw(ax=ax)
    # 'half=True' ensures clipping to half court dimensions
    court.hexbin(ax, x, y, gridsize=15, cmap='bsu_blue', mincnt=1, 
                 half=True, edgecolors='white', linewidths=0.5)
    plt.title("Hexbin Plot (Half Clipped)")
    plt.savefig("test_heatmap_hex_half.png")
    plt.close()

if __name__ == "__main__":
    try:
        test_heatmap()
        print("Heatmap tests passed!")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
