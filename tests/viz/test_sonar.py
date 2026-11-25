
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from bsutennis import TennisCourt
from bsutennis.viz.sonar import sonar_chart, sonar_from_shots, create_zone_grid

def test_sonar():
    print("Testing Sonar Charts...")
    
    # Generate mock shot data
    np.random.seed(42)
    n_shots = 200
    
    # Shot origins (from baseline area)
    shot_x = np.random.uniform(-3.5, 3.5, n_shots)
    shot_y = np.random.uniform(1, 10, n_shots)
    
    # Shot directions (random but biased forward/cross-court)
    shot_dx = np.random.normal(0, 2, n_shots) - shot_x * 0.3  # Slight cross bias
    shot_dy = np.random.normal(3, 2, n_shots)  # Forward bias
    
    # 1. Sonar from raw shot data (Half Court)
    print("  Creating sonar from shot data...")
    court = TennisCourt(orientation='vertical', half=True, theme='bsu')
    fig, ax = plt.subplots(figsize=(8, 10))
    court.draw(ax=ax)
    
    sonar_from_shots(ax, shot_x, shot_y, shot_dx, shot_dy,
                     court=court, n_zones_x=3, n_zones_y=2,
                     n_directions=6, zone_size=1.5, half=True,
                     cmap='bsu')
    
    plt.title("Shot Direction Sonar (6 Directions)", fontsize=14, fontweight='bold', pad=10)
    plt.savefig("test_sonar_6dir.png", dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("    Created test_sonar_6dir.png")
    
    # 2. Sonar with 8 directions
    print("  Creating 8-direction sonar...")
    court = TennisCourt(orientation='vertical', half=True, theme='bsu')
    fig, ax = plt.subplots(figsize=(8, 10))
    court.draw(ax=ax)
    
    sonar_from_shots(ax, shot_x, shot_y, shot_dx, shot_dy,
                     court=court, n_zones_x=3, n_zones_y=2,
                     n_directions=8, zone_size=1.3, half=True,
                     cmap='cool')
    
    plt.title("Shot Direction Sonar (8 Directions)", fontsize=14, fontweight='bold', pad=10)
    plt.savefig("test_sonar_8dir.png", dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("    Created test_sonar_8dir.png")
    
    # 3. Manual zone data example
    print("  Creating manual zone sonar...")
    court = TennisCourt(orientation='vertical', half=True, theme='bsu')
    fig, ax = plt.subplots(figsize=(8, 10))
    court.draw(ax=ax)
    
    # Define zones manually with custom direction data
    zone_data = [
        {'x': -2.5, 'y': 3, 'directions': [10, 25, 35, 15, 10, 5]},   # Left baseline
        {'x': 0, 'y': 3, 'directions': [15, 20, 30, 20, 10, 5]},      # Center baseline
        {'x': 2.5, 'y': 3, 'directions': [5, 10, 15, 35, 25, 10]},    # Right baseline
        {'x': -2, 'y': 8, 'directions': [20, 30, 25, 10, 10, 5]},     # Left mid
        {'x': 2, 'y': 8, 'directions': [5, 10, 10, 25, 30, 20]},      # Right mid
    ]
    
    sonar_chart(ax, zone_data, court=court, n_directions=6, 
                zone_size=1.6, cmap='bsu', show_labels=True)
    
    plt.title("Custom Zone Sonar Analysis", fontsize=14, fontweight='bold', pad=10)
    plt.savefig("test_sonar_custom.png", dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("    Created test_sonar_custom.png")

if __name__ == "__main__":
    try:
        test_sonar()
        print("Sonar chart tests passed!")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
