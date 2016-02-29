import heapq
import math


def cube_round(h):
    """Round cubic hexagonal coordinates to an integer cubic tile."""
    x, y, z = h
    rx = round(x)
    ry = round(y)
    rz = round(z)

    x_diff = abs(rx - x)
    y_diff = abs(ry - y)
    z_diff = abs(rz - z)

    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry - rz
    elif y_diff > z_diff:
        ry = -rx - rz
    else:
        rz = -rx - ry

    return rx, ry, rz


def cube_to_hex(h):
    """Convert a 3-tuple of cubic coords to 2 "even-q vertical" coords."""
    x, _, z = h
    return x, z + (x + (int(x) % 2)) // 2


def hex_to_cube(h):
    """Convert a 2-tuple of "even-q vertical" coords to cubic coords."""
    c, r = h

    x = c
    z = r - (c + (int(c) % 2)) // 2
    return (
        x,
        -x - z,
        z
    )


def hex_round(h):
    return cube_to_hex(cube_round(hex_to_cube(h)))


root3 = 3 ** 0.5

HEX_WIDTH = 128
HEX_HEIGHT = 48


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


def heuristic(a, b):
    """Get the distance between points a and b."""
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


class NoPath(Exception):
    """There is no route to the goal."""


class HexGrid:
    def __init__(self):
        self.cells = {}

    def __setitem__(self, coords, value):
        self.cells[coords] = value

    def __getitem__(self, coords):
        return self.cells.get(coords)

    def __contains__(self, coords):
        return bool(self.cells.get(coords))

    NEIGHBOURS_EVEN = [
        (0, -1),
        (1, 0),
        (1, 1),
        (0, 1),
        (-1, 1),
        (-1, 0),
    ]
    NEIGHBOURS_ODD = [
        (0, -1),
        (1, -1),
        (1, 0),
        (0, 1),
        (-1, 0),
        (-1, -1)
    ]

    @staticmethod
    def coord_to_world(coord):
        """Convert a map coordinate to a Cartesian world coordinate."""
        cx, cy = coord
        wx = 3/2 * cx
        wy = root3 * (cy - 0.5 * (cx & 1))
        return wx, wy

    @staticmethod
    def coord_to_screen(coord):
        """Convert a map coordinate to screen coordinates."""
        wx, wy = HexGrid.coord_to_world(coord)
        return (
            wx * HEX_WIDTH / 2,
            wy * HEX_HEIGHT / 2
        )

    @staticmethod
    def screen_to_coord(coord):
        """Get the map coordinates for a screen pixel (x, y)."""
        x, y = coord
        x /= HEX_WIDTH / 2
        y /= HEX_HEIGHT / 2
        q = x * (2 / 3)
        r = -x / 3 + root3 / 3 * y
        return cube_to_hex(cube_round((q, -q - r, r)))

    def neighbours(self, coords):
        """Iterate over the neighbour of the given coords.

        Note that we use an "even-q vertical" layout in the terminology of
        http://www.redblobgames.com/grids/hexagons/#coordinates

        """
        x, y = coords
        neighbours = self.NEIGHBOURS_ODD if x % 2 else self.NEIGHBOURS_EVEN
        for dx, dy in neighbours:
            c = x + dx, y + dy
            if c in self:
                yield c

    @staticmethod
    def distance(a, b):
        """Calculate the distance between two pairs of coordinates."""
        ax, ay = HexGrid.coord_to_world(a)
        bx, by = HexGrid.coord_to_world(b)
        dx = ax - bx
        dy = ay - by
        return math.sqrt(dx * dx + dy * dy)

    def find_path(self, start, goal):
        """Find a path from start to goal using A*.

        This can be quite expensive if goal is unreachable.

        """
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == goal:
                break

            for next in self.neighbours(current):
                new_cost = cost_so_far[current] + self.distance(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current
        else:
            raise NoPath(start, goal)

        path = [goal]
        while current != start:
            current = came_from[current]
            path.append(current)
        return path
        #return came_from, cost_so_far
