import unittest
from collections import Counter

# Edges := [Edge*]
# Edge := (Vertex, Vertex)
# Vertex := Hashable except None

def solve_hitofude(edges):
    def _make_vertexcounter(edges):
        c = Counter()
        for x, y in edges:
            c[x] += 1
            c[y] += 1
        return c

    def _make_edgeflag(edges, value=True):
        d = dict()
        for edge in edges:
            d[edge] = value
        return d

    def _get_head_tail(counter):
        odd = []
        for k,v in counter.items():
            if v&1: odd.append(k)
        if len(odd) == 2:
            return tuple(odd)
        elif len(odd) == 0:
            t = c.most_common(1)[0][0]
            return t, t
        else:
            return None, None

    def _edge_selector(pos, edgeflag):
        for edge in edgeflag:
            if edgeflag[edge]:
                a, b = edge
                if a == pos:
                    yield edge, b
                if edgeflag[edge] and b == pos:
                    yield edge, a

    stack_pos = []
    stack_edge = []
    stack_selector = []

    c = _make_vertexcounter(edges)
    remain = _make_edgeflag(edges)

    pos, tail = _get_head_tail(c)
    if pos is None:
        return None
    n = len(edges)
    selector = _edge_selector(pos, remain)

    while n:
        try:
            edge, nextpos = next(selector)
        except StopIteration:
            if stack_pos:
                pos = stack_pos.pop()
                remain[stack_edge.pop()] = True
                selector = stack_selector.pop()
                n += 1
            else:
                return None
        else:
            stack_pos.append(pos)
            stack_edge.append(edge)
            stack_selector.append(selector)
            pos = nextpos
            remain[edge] = False
            selector = _edge_selector(pos, remain)
            n -= 1
    if pos == tail:
        return stack_pos, stack_edge
    assert False


class HitofudeTest(unittest.TestCase):
    def test_has_answer_or_not(self):
        cases = [
            ([(1,2),(2,3),(3,1),(2,4),(4,5),(5,3),(2,5),(3,4)],True),
            ([(1,2),(3,1),(2,4),(4,5),(5,3),(2,5),(3,4)],False),
            ([(1,5),(1,4),(2,3),(2,4),(3,5)],True),
            ([(1,2),(2,3),(3,1),(4,5),(5,6),(6,4)],False)
        ]

        for edges, has_answer in cases:
            if has_answer:
                self.assertIsNotNone(solve_hitofude(edges))
            else:
                self.assertIsNone(solve_hitofude(edges))

if __name__ == '__main__':
    unittest.main()
