
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from bsutennis import TennisCourt

def test_plot():
    # 1. Standard Horizontal Doubles
    print("Testing Standard Horizontal Doubles...")
    court = TennisCourt(theme='bsu')
    fig, ax = plt.subplots(figsize=(10, 6))
    court.draw(ax=ax)
    plt.title("Tennis Court (Doubles - Horizontal)")
    plt.savefig("test_horizontal_doubles.png")
    plt.close()

    # 2. Vertical Singles
    print("Testing Vertical Singles...")
    court_v = TennisCourt(court_type='doubles', orientation='vertical', theme='bsu')
    fig, ax = plt.subplots(figsize=(6, 10))
    court_v.draw(ax=ax)
    plt.title("Tennis Court (Singles - Vertical)")
    plt.savefig("test_vertical_singles.png")
    plt.close()
    
    # 3. Half Vertical Doubles with Service Zones (2 Lines)
    print("Testing Half Vertical Doubles with Zones...")
    court_hv = TennisCourt(court_type='doubles', orientation='vertical', half=True, theme='bsu')
    fig, ax = plt.subplots(figsize=(6, 6))
    court_hv.draw(ax=ax)
    # 2 lines in service zone (Trisect), No backcourt line
    court_hv.draw_guides(ax, service_vertical_lines=2, backcourt_line=False)
    plt.title("Half Vertical (2 Service Lines)")
    plt.savefig("test_half_vertical_zones.png")
    plt.close()
    
    # 4. Half Horizontal Doubles with Zones (1 Line + Backcourt)
    print("Testing Half Horizontal Doubles with Zones...")
    court_hh = TennisCourt(court_type='doubles', orientation='horizontal', half=True, theme='bsu')
    fig, ax = plt.subplots(figsize=(6, 6))
    court_hh.draw(ax=ax)
    # 1 line in service zone (Bisect), With backcourt line
    court_hh.draw_guides(ax, service_vertical_lines=1, backcourt_line=True)
    plt.title("Half Horizontal (1 Service Line + Backcourt)")
    plt.savefig("test_half_horizontal_zones.png")
    plt.close()

if __name__ == "__main__":
    try:
        test_plot()
        print("Test passed!")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
