import matplotlib.pyplot as plt
import matplotlib.patches as patches


def draw_full_court(color_scheme=None):
    """绘制整个网球场"""
    if color_scheme is None:
        color_scheme = {"court": "green", "lines": "white", "net": "black"}

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 23.77)  # 网球场长度 (米)
    ax.set_ylim(0, 10.97)  # 双打宽度 (米)

    # 绘制球场背景
    court = patches.Rectangle((0, 0), 23.77, 10.97, color=color_scheme["court"])
    ax.add_patch(court)

    # 绘制双打边界线
    ax.plot([0, 23.77], [0, 0], color=color_scheme["lines"])
    ax.plot([0, 23.77], [10.97, 10.97], color=color_scheme["lines"])
    ax.plot([0, 0], [0, 10.97], color=color_scheme["lines"])
    ax.plot([23.77, 23.77], [0, 10.97], color=color_scheme["lines"])

    # 绘制单打边线
    ax.plot([0, 23.77], [1.37, 1.37], color=color_scheme["lines"])
    ax.plot([0, 23.77], [9.60, 9.60], color=color_scheme["lines"])

    # 绘制服务线和中线
    ax.plot([5.49, 5.49], [1.37, 9.60], color=color_scheme["lines"])
    ax.plot([18.28, 18.28], [1.37, 9.60], color=color_scheme["lines"])
    ax.plot([11.89, 11.89], [0, 10.97], color=color_scheme["lines"])

    # 绘制网
    ax.plot([11.89, 11.89], [0, 10.97], color=color_scheme["net"], linestyle="--")

    ax.set_aspect("equal")
    ax.axis("off")
    plt.show()


def draw_half_court(color_scheme=None):
    """绘制半个网球场"""
    if color_scheme is None:
        color_scheme = {"court": "green", "lines": "white", "net": "black"}

    fig, ax = plt.subplots(figsize=(5, 6))
    ax.set_xlim(0, 11.89)  # 半场长度
    ax.set_ylim(0, 10.97)

    court = patches.Rectangle((0, 0), 11.89, 10.97, color=color_scheme["court"])
    ax.add_patch(court)

    ax.plot([0, 11.89], [0, 0], color=color_scheme["lines"])
    ax.plot([0, 11.89], [10.97, 10.97], color=color_scheme["lines"])
    ax.plot([0, 0], [0, 10.97], color=color_scheme["lines"])
    ax.plot([11.89, 11.89], [0, 10.97], color=color_scheme["lines"])
    ax.plot([0, 11.89], [1.37, 1.37], color=color_scheme["lines"])
    ax.plot([0, 11.89], [9.60, 9.60], color=color_scheme["lines"])
    ax.plot([5.49, 5.49], [1.37, 9.60], color=color_scheme["lines"])
    ax.plot([11.89, 11.89], [0, 10.97], color=color_scheme["net"], linestyle="--")

    ax.set_aspect("equal")
    ax.axis("off")
    plt.show()


def draw_three_courts(color_scheme=None):
    """绘制三个并排的整个网球场"""
    if color_scheme is None:
        color_scheme = {"court": "green", "lines": "white", "net": "black"}

    fig, ax = plt.subplots(figsize=(15, 15))
    ax.set_xlim(0, 23.77 * 3)
    ax.set_ylim(0, 10.97)

    for i in range(3):
        x_offset = i * 23.77
        court = patches.Rectangle(
            (x_offset, 0), 23.77, 10.97, color=color_scheme["court"]
        )
        ax.add_patch(court)
        ax.plot([x_offset, x_offset + 23.77], [0, 0], color=color_scheme["lines"])
        ax.plot(
            [x_offset, x_offset + 23.77], [10.97, 10.97], color=color_scheme["lines"]
        )
        ax.plot([x_offset, x_offset], [0, 10.97], color=color_scheme["lines"])
        ax.plot(
            [x_offset + 23.77, x_offset + 23.77],
            [0, 10.97],
            color=color_scheme["lines"],
        )
        ax.plot([x_offset, x_offset + 23.77], [1.37, 1.37], color=color_scheme["lines"])
        ax.plot([x_offset, x_offset + 23.77], [9.60, 9.60], color=color_scheme["lines"])
        ax.plot(
            [x_offset + 5.49, x_offset + 5.49],
            [1.37, 9.60],
            color=color_scheme["lines"],
        )
        ax.plot(
            [x_offset + 18.28, x_offset + 18.28],
            [1.37, 9.60],
            color=color_scheme["lines"],
        )
        ax.plot(
            [x_offset + 11.89, x_offset + 11.89],
            [0, 10.97],
            color=color_scheme["lines"],
        )
        ax.plot(
            [x_offset + 11.89, x_offset + 11.89],
            [0, 10.97],
            color=color_scheme["net"],
            linestyle="--",
        )

    ax.set_aspect("equal")
    ax.axis("off")
    plt.show()
