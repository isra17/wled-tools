import pyglet
from pyglet import shapes
import math

INNER_SIZE = 80
MIDDLE_SIZE = 100
OUTER_MIDDLE_SIZE = 105
OUTER_SIZE = 100
START = (250, 490)
CENTER = (250, 250)

def vec_add(*args):
    return list(map(sum, zip(*args)))

def generate():
    lines = []
    pos = START
    angle = 102 * math.pi / 180

    for i in range(15):
        end = vec_add(pos, (math.sin(angle) * OUTER_SIZE, math.cos(angle) * OUTER_SIZE))
        lines.append((pos, end))
        angle += (2 * math.pi / 15)
        pos = end

    pos = CENTER
    for i in range(5):
        angle = i * (2 * math.pi / 5)
        end = vec_add(pos, (math.sin(angle) * INNER_SIZE, math.cos(angle) * INNER_SIZE))
        lines.append((pos, end))

        angle = (i+1) * (2 * math.pi / 5)
        other_end = vec_add(pos, (math.sin(angle) * INNER_SIZE, math.cos(angle) * INNER_SIZE))
        lines.append((end, other_end))

        angle = i * (2 * math.pi / 5)
        second_end = vec_add(end, (math.sin(angle) * MIDDLE_SIZE, math.cos(angle) * MIDDLE_SIZE))
        lines.append((end, second_end))

        angle = i * (2 * math.pi / 5) + (68 * math.pi/180)
        outer_end = vec_add(second_end, (math.sin(angle) * OUTER_MIDDLE_SIZE, math.cos(angle) * OUTER_MIDDLE_SIZE))
        lines.append((second_end, outer_end))

        angle = i * (2 * math.pi / 5) - (68 * math.pi/180)
        outer_end = vec_add(second_end, (math.sin(angle) * OUTER_MIDDLE_SIZE, math.cos(angle) * OUTER_MIDDLE_SIZE))
        lines.append((second_end, outer_end))



    return lines

def display_dome():
    lines = generate()

    window = pyglet.window.Window(500, 500)

    label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

    batch = pyglet.graphics.Batch()
    batch_items = []
    for (start, end) in lines:
        batch_items.append(shapes.Line(*start, *end, width=2, color=(255, 0, 0), batch=batch))

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    pyglet.app.run()


if __name__ == '__main__':
    display_dome()

