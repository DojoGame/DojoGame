from dojogame.dojographics.gameobjects import *
from dojogame.dojomaths.vectors import *


class Collision:
    def __init__(self, collide: bool, point: Vector2 = None, normal: Vector2 = None):
        self.collide = collide
        self.point = point
        self.normal = normal

    def __bool__(self):
        return self.collide


class AxisAlignedBoundingBox:
    def __init__(self, obj: Polygon | Circle):
        self.obj = obj
        self.min_v = self.max_v = Vector2.zero()
        self.update_aabb()

    def update_aabb(self):
        if isinstance(self.obj, Polygon):
            vertices = self.obj.get_absolute_vertices_positions()
            max_x = max_y = float("-inf")
            min_x = min_y = float("inf")
            for vertex in vertices:
                if vertex.x > max_x:
                    max_x = vertex.x
                if vertex.y > max_y:
                    max_y = vertex.y
                if vertex.x < min_x:
                    min_x = vertex.x
                if vertex.y < min_y:
                    min_y = vertex.y
            self.min_v = Vector2(min_x, min_y)
            self.max_v = Vector2(max_x, max_y)
        elif isinstance(self.obj, Circle):
            self.min_v = self.obj.transform.position - Vector2(self.obj.radius, self.obj.radius)
            self.max_v = self.obj.transform.position + Vector2(self.obj.radius, self.obj.radius)
        else:
            raise TypeError("Wrong type of object given")

    def aabb_overlap(self, other: 'AxisAlignedBoundingBox') -> bool:
        return self.min_v.x < other.max_v.x and self.max_v.x > other.min_v.x and \
               self.min_v.y < other.max_v.y and self.max_v.y > other.min_v.y


AABB = AxisAlignedBoundingBox


class Collisions:
    @staticmethod
    def intersect_polygons(p1: Polygon, p2: Polygon) -> Collision:
        if not p1.get_collider().aabb.aabb_overlap(p2.get_collider().aabb):
            return Collision(False)

        def find_arithmetic_mean(points: list) -> Vector2:
            x = y = 0

            for j in range(len(points)):
                x += points[j].x
                y += points[j].y
            return Vector2(x / len(points), y / len(points))

        vertices_a = p1.get_absolute_vertices_positions()
        vertices_b = p2.get_absolute_vertices_positions()

        normal = Vector2.zero()
        depth = float('inf')

        for i in range(len(vertices_a)):
            va = vertices_a[i]
            vb = vertices_a[(i + 1) % len(vertices_a)]

            edge = vb - va
            axis = Vector2(-edge.y, edge.x)

            (min_a, max_a) = Collisions.project_vertices(vertices_a, axis)
            (min_b, max_b) = Collisions.project_vertices(vertices_b, axis)

            if min_a >= max_b or min_b >= max_a:
                return Collision(False)

            axis_depth = min(max_a - min_b, max_b - min_a)

            if axis_depth < depth:
                depth = axis_depth
                normal = axis

        for i in range(len(vertices_b)):
            va = vertices_b[i]
            vb = vertices_b[(i + 1) % len(vertices_b)]

            edge = vb - va
            axis = Vector2(-edge.y, edge.x)

            (min_a, max_a) = Collisions.project_vertices(vertices_a, axis)
            (min_b, max_b) = Collisions.project_vertices(vertices_b, axis)

            if min_a >= max_b or min_b >= max_a:
                return Collision(False)

            axis_depth = min(max_a - min_b, max_b - min_a)

            if axis_depth < depth:
                depth = axis_depth
                normal = axis

        center_a = find_arithmetic_mean(vertices_a)
        center_b = find_arithmetic_mean(vertices_b)

        direction = center_b - center_a

        if Vector2.dot(direction, normal) < 0:
            normal = -normal
        return Collision(True, normal=normal)

    @staticmethod
    def project_vertices(vertices: list, axis: Vector2) -> tuple:
        _min = Vector2.dot(vertices[0], axis)
        _max = _min
        for v in vertices:
            p = Vector2.dot(v, axis)
            if p < _min:
                _min = p
            elif p > _max:
                _max = p
        return _min, _max


class Collider:
    def collide_with(self, other) -> Collision:
        raise NotImplementedError

    @staticmethod
    def add_collider(go: GameObject):
        if isinstance(go, Polygon):
            go.collider = PolygonCollider(go)
        elif isinstance(go, Circle):
            go.collider = CircleCollider(go)
        else:
            raise TypeError("Wrong type of object given")


class PolygonCollider(Collider):
    def __init__(self, polygon: Polygon):
        self.polygon = polygon
        self.aabb = AABB(polygon)

    def collide_with(self, other: Collider) -> bool:
        if other is None:
            return False
        if isinstance(other, PolygonCollider):
            return bool(Collisions.intersect_polygons(self.polygon, other.polygon))
        else:
            raise NotImplementedError


class CircleCollider(Collider):
    def __init__(self, circle: Circle):
        self.circle = circle
        self.aabb = AABB(circle)

    def collide_with(self, other) -> Collision:
        raise NotImplementedError