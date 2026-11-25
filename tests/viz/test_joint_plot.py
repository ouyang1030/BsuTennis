
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from bsutennis import joint_plot

def test_joint_plots():
    print("Testing Joint Plots...")
    
    # Generate realistic shot data for two players
    np.random.seed(42)
    
    # Player A shots (left side of court, y < 0 in standard coords)
    # Shots landing on opponent's side
    player_a_x = np.concatenate([
        np.random.normal(-2, 1.5, 50),  
        np.random.normal(2, 1.5, 50),   
    ])
    player_a_y = np.concatenate([
        np.random.normal(8, 2, 50),      # Deep shots
        np.random.normal(7, 2.5, 50),    # Mid-deep shots
    ])
    # Clip to court boundaries
    player_a_x = np.clip(player_a_x, -5.485, 5.485)  # Doubles width
    player_a_y = np.clip(player_a_y, 0, 11.89)
    
    # Player B shots (right side of court, y > 0 in standard coords)
    player_b_x = np.concatenate([
        np.random.normal(-1.5, 1.8, 50),
        np.random.normal(1.5, 1.8, 50),
    ])
    player_b_y = np.concatenate([
        np.random.normal(-8, 2, 50),     # Deep shots to opponent
        np.random.normal(-6, 2.5, 50),   # Mid shots
    ])
    player_b_x = np.clip(player_b_x, -5.485, 5.485)
    player_b_y = np.clip(player_b_y, -11.89, 0)
    
    # 1. Full Court Tests
    print("Testing Full Court KDE...")
    fig, ax = joint_plot(
        player_a_x, player_a_y,
        player_b_x, player_b_y,
        kind='kde',
        half=False,
        color1='#92e3da',
        color2='#9b59b6',
        label1='Player A',
        label2='Player B',
        theme='bsu',
        figsize=(14, 8)
    )
    plt.savefig("test_joint_kde.png", dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # 2. Half Court Tests
    print("Testing Half Court Scatter...")
    fig, ax = joint_plot(
        player_a_x, player_a_y,
        kind='scatter',
        half=True,
        color1='#92e3da',
        label1='Player A',
        theme='bsu',
        figsize=(8, 8)
    )
    plt.savefig("test_joint_half_scatter.png", dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    print("Testing Half Court KDE...")
    fig, ax = joint_plot(
        player_a_x, player_a_y,
        kind='kde',
        half=True,
        color1='#92e3da',
        label1='Player A',
        theme='bsu',
        figsize=(8, 8)
    )
    plt.savefig("test_joint_half_kde.png", dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # 3. Grid Visualization
    print("Testing Half Court Grid...")
    fig, ax = joint_plot(
        player_a_x, player_a_y,
        kind='grid',
        half=True,
        color1='#92e3da',
        label1='Player A',
        figsize=(8, 8), 
        grid_bins=(8, 4)
    )
    plt.savefig("test_joint_grid.png", dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("Joint plot tests passed!")

if __name__ == "__main__":
    try:
        test_joint_plots()
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
