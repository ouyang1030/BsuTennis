
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from bsutennis import pizza_chart, pizza

def test_pizza():
    print("Testing Pizza Charts...")
    
    # 1. BSU Theme Pizza Chart
    stats = {
        'Aces': 85,
        'Double Faults': 35,
        '1st Serve %': 72,
        '1st Serve Won': 78,
        '2nd Serve Won': 55,
        'Break Points Saved': 68,
        'Winners': 82,
        'Unforced Errors': 40,
    }
    
    fig, ax = pizza(
        'Jannik Sinner',
        stats,
        theme='bsu',
        figsize=(10, 10)
    )
    plt.savefig("test_pizza_bsu.png", dpi=150, bbox_inches='tight', facecolor='#0d1b2a')
    plt.close()
    print("  Created test_pizza_bsu.png")
    
    # 2. Comparison Pizza (Player vs Average)
    params = ['Serve Speed', 'Return Depth', 'Net Approach', 
              'Baseline Rally', 'Drop Shots', 'Lob Success']
    player_values = [92, 78, 65, 88, 45, 72]
    avg_values = [75, 70, 55, 75, 50, 60]
    
    fig, ax = pizza_chart(
        params, player_values,
        title='Novak\nDjokovic',
        compare_values=avg_values,
        compare_label='Tour Average',
        theme='dark',
        figsize=(10, 10)
    )
    plt.savefig("test_pizza_compare.png", dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    print("  Created test_pizza_compare.png")

if __name__ == "__main__":
    try:
        test_pizza()
        print("Pizza chart tests passed!")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()


def test_slices_scale_with_the_value():
    """A value of 100 reaches the outer edge, inside the axes; 50 goes halfway."""
    from matplotlib.patches import Rectangle

    fig, ax = pizza_chart(["a", "b"], [100, 50], inner_circle_size=0.4)
    slices = [p for p in ax.patches if isinstance(p, Rectangle)]
    tops = [s.get_y() + s.get_height() for s in slices]
    assert tops == [1.0, 0.7]
    assert ax.get_ylim()[1] > max(tops)
