
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from bsutennis import TennisCourt, THEMES

def test_themes():
    print("Testing Themes...")
    
    # 1. BSU Theme
    print(" - BSU Theme")
    court = TennisCourt(theme='bsu', orientation='horizontal')
    fig, ax = plt.subplots(figsize=(10, 6))
    court.draw(ax=ax)
    court.draw_bsu_guides(ax) # Add guides
    plt.title("BSU Theme (White/Black)")
    plt.savefig("test_theme_bsu.png", dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Hard Court
    print(" - Hard Court")
    court = TennisCourt(theme='hard', orientation='horizontal')
    fig, ax = plt.subplots(figsize=(10, 6))
    court.draw(ax=ax)
    plt.title("Hard Court")
    plt.savefig("test_theme_hard.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # 3. Clay Court
    print(" - Clay Court")
    court = TennisCourt(theme='clay', orientation='horizontal')
    fig, ax = plt.subplots(figsize=(10, 6))
    court.draw(ax=ax)
    plt.title("Clay Court")
    plt.savefig("test_theme_clay.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # 4. Grass Court
    print(" - Grass Court")
    court = TennisCourt(theme='grass', orientation='horizontal')
    fig, ax = plt.subplots(figsize=(10, 6))
    court.draw(ax=ax)
    plt.title("Grass Court")
    plt.savefig("test_theme_grass.png", dpi=150, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    try:
        test_themes()
        print("Theme tests passed!")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
