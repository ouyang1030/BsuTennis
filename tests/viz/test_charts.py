
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from bsutennis import plot_bar, plot_bar_comparison, plot_horizontal_bar, plot_line, plot_pie, plot_table

def test_charts():
    print("Testing Charts...")
    
    # 1. Bar Chart
    print("- Bar Chart")
    fig, ax = plt.subplots(figsize=(6, 4))
    plot_bar(ax, ['A', 'B', 'C'], [10, 20, 15], title="Simple Bar")
    plt.savefig("test_chart_bar.png")
    plt.close()
    
    # 2. Bar Comparison (Moving Bar)
    print("- Bar Comparison")
    fig, ax = plt.subplots(figsize=(8, 4))
    plot_bar_comparison(ax, ['Short', 'Medium', 'Long'], [5, 12, 3], [4, 10, 5], 
                        label1='Player', label2='Opponent', title="Distance Stats")
    plt.savefig("test_chart_comparison.png")
    plt.close()
    
    # 3. Horizontal Bar
    print("- Horizontal Bar")
    fig, ax = plt.subplots(figsize=(6, 4))
    plot_horizontal_bar(ax, ['Cat1', 'Cat2', 'Cat3'], [50, 30, 80], title="Horizontal")
    plt.savefig("test_chart_horizontal.png")
    plt.close()
    
    # 4. Line Chart
    print("- Line Chart")
    fig, ax = plt.subplots(figsize=(6, 4))
    plot_line(ax, [1, 2, 3, 4], [10, 15, 13, 18], title="Trend")
    plt.savefig("test_chart_line.png")
    plt.close()
    
    # 5. Pie Chart
    print("- Pie Chart")
    fig, ax = plt.subplots(figsize=(4, 4))
    plot_pie(ax, [30, 20, 50], ['Win', 'Loss', 'Other'], title="Pie")
    plt.savefig("test_chart_pie.png")
    plt.close()
    
    # 6. Table
    print("- Table")
    fig, ax = plt.subplots(figsize=(6, 2))
    plot_table(ax, [['10', '20'], ['30', '40']], columns=['Col1', 'Col2'], rows=['Row1', 'Row2'])
    plt.savefig("test_chart_table.png")
    plt.close()

if __name__ == "__main__":
    try:
        test_charts()
        print("Chart tests passed!")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
