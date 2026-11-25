
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

def _setup_axis(ax):
    """Helper to styling axis similar to user's reports."""
    if ax is None:
        ax = plt.gca()
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    return ax

def plot_bar(ax, categories, values, color='#66DCE3', title=None, xlabel=None, ylabel=None, **kwargs):
    """
    Standard vertical bar chart.
    """
    ax = _setup_axis(ax)
    
    x = np.arange(len(categories))
    bars = ax.bar(x, values, color=color, **kwargs)
    
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    
    if title: ax.set_title(title, fontsize=14)
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}' if isinstance(height, float) else f'{height}',
                ha='center', va='bottom')
                
    return bars

def plot_bar_comparison(ax, categories, values1, values2, label1='Player 1', label2='Player 2',
                        color1='#66DCE3', color2='#9F9F9F', title=None, **kwargs):
    """
    Side-by-side bar chart (Moving Bar Chart style).
    """
    ax = _setup_axis(ax)
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, values1, width, label=label1, color=color1, **kwargs)
    bars2 = ax.bar(x + width/2, values2, width, label=label2, color=color2, **kwargs)
    
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    
    if title: ax.set_title(title, fontsize=14)
    ax.legend(frameon=False)
    
    # Value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                 ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}' if isinstance(height, float) else f'{height}',
                        ha='center', va='bottom', fontsize=8)

    return bars1, bars2

def plot_horizontal_bar(ax, categories, values, color='#EB8686', title=None, **kwargs):
    """
    Horizontal bar chart.
    """
    ax = _setup_axis(ax)
    
    y = np.arange(len(categories))
    bars = ax.barh(y, values, color=color, **kwargs)
    
    ax.set_yticks(y)
    ax.set_yticklabels(categories)
    
    if title: ax.set_title(title, fontsize=14)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2,
                f' {width:.1f}' if isinstance(width, float) else f' {width}',
                ha='left', va='center')
                
    return bars

def plot_line(ax, x, y, color='#66DCE3', marker='o', title=None, **kwargs):
    """
    Standard line chart.
    """
    ax = _setup_axis(ax)
    
    line = ax.plot(x, y, color=color, marker=marker, linewidth=2, **kwargs)
    
    if title: ax.set_title(title, fontsize=14)
    
    return line

def plot_pie(ax, values, labels, colors=None, title=None, **kwargs):
    """
    Pie chart.
    """
    if ax is None:
        ax = plt.gca()
        
    if colors is None:
        colors = ['#66DCE3', 'silver', '#EB8686', '#778BEB', '#C5E0B3']
        
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors[:len(values)],
                                      startangle=90, textprops={'fontsize': 10}, **kwargs)
                                      
    if title: ax.set_title(title)
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')  
    
    return wedges

def plot_table(ax, data, columns=None, rows=None, loc='center', **kwargs):
    """
    Table.
    """
    if ax is None:
        ax = plt.gca()
        
    ax.axis('off')
    
    table = ax.table(cellText=data, colLabels=columns, rowLabels=rows, loc=loc, cellLoc='center', **kwargs)
    table.scale(1, 1.5)
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    
    return table
