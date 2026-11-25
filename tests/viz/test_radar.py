
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from bsutennis import Radar

def test_radar():
    print("Testing Radar Chart...")
    
    # Define parameters
    params = ['Serve Speed\n(km/h)', 'First Serve\n(%)', 'Aces\n(per match)', 
              'Winners\n(per match)', 'Break Points\nWon (%)', 'Rally\nLength']
    
    # Define ranges
    min_range = [150, 50, 0, 20, 30, 3]
    max_range = [220, 80, 15, 60, 70, 8]
    
    # Create radar instance
    radar = Radar(params, min_range=min_range, max_range=max_range)
    
    # Setup axis
    fig, ax = radar.setup_axis(figsize=(10, 10))
    
    # Draw background circles
    radar.draw_circles(ax, num_rings=5, color='#d3d3d3', linewidth=1)
    
    # Player A data
    player_a_values = [205, 68, 12, 48, 55, 6.5]
    radar.draw(ax, player_a_values, label='Player A', color='#e74c3c', alpha=0.25, linewidth=2.5)
    
    # Player B data
    player_b_values = [195, 72, 8, 52, 62, 5.8]
    radar.draw(ax, player_b_values, label='Player B', color='#3498db', alpha=0.25, linewidth=2.5)
    
    # Add legend
    plt.legend(loc='upper right', bbox_to_anchor=(1.25, 1.1), fontsize=12, frameon=True, fancybox=True)
    
    # Add title
    plt.title('Player Performance Comparison', size=16, weight='bold', pad=20)
    
    # Save
    plt.tight_layout()
    plt.savefig("test_radar.png", dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

if __name__ == "__main__":
    try:
        test_radar()
        print("Radar test passed!")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
