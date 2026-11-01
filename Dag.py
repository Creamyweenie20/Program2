from collections import deque 
import json 


class Node:
    def __init__(self, id, op, result=None):
        self.id = id
        self.op = op 
        self.result = result 
        self.parent = []
        self.child = []

    def __repr__(self): 
        return f"Node({self.id}, {self.op!r}, {self.result!r})"


class DAG: 
    def __init__(self): 
        self.nodes = []
        self.defs = {}

    def _new_node(self, op, result = None): 
        node = Node(len(self.nodes), op, result)
        self.nodes.append(node)
        if result: 
            self.defs[result] = node
        return node 

    def _get_operand(self, token): 
        if token in self.defs: 
            return self.defs[token]

        op = 'const' if token.lstrip("-").isdigit() else "input"

        return self._new_node(op, token)

    def add_statemnt(self, line): 
        lhs, rhs = [s.strip() for s in line.split("=")]
        left, op, right = rhs.split()

        sources = [self._get_operand(left), self._get_operand(right)]

        node = self._new_node(op, lhs) 
        for src in sources: 
            node.parent.append(src)
            src.child.append(node)
        return node


    def topo_order(self):
        # Kahn's algorithm: repeatedly take nodes with no unprocessed dependencies
        remaining = {n.id: len(n.parent) for n in self.nodes}
        ready = deque(n for n in self.nodes if remaining[n.id] == 0)
        order = []

        while ready:
            node = ready.popleft()
            order.append(node)
            for s in node.child:
                remaining[s.id] -= 1
                if remaining[s.id] == 0:
                    ready.append(s)

        if len(order) != len(self.nodes):
            raise ValueError("Graph has a cycle")
        return order

    def to_dot(self):
        lines = ["digraph G {"]
        for n in self.nodes:
            lines.append(f'  {n.id} [label="{n.op}\\n{n.result or ""}"];')
        for n in self.nodes:
            for s in n.child:
                lines.append(f"  {n.id} -> {s.id};")
        lines.append("}")
        return "\n".join(lines)

    def to_dict(self):
        return {
            "nodes": [
                {
                    "id": n.id,
                    "op": n.op,
                    "result": n.result,
                    "parents": [p.id for p in n.parent],
                    "children": [c.id for c in n.child],
                }
                for n in self.nodes
            ]
        }

    def save_json(self, path="DAG.json"):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def levels(self):
        # level = longest path from any input to this node
        level = {}
        for n in self.topo_order():
            if not n.parent:
                level[n.id] = 0
            else:
                level[n.id] = 1 + max(level[p.id] for p in n.parent)
        return level

    def print_levels(self):
        level = self.levels()
        columns = {}
        for n in self.nodes:
            columns.setdefault(level[n.id], []).append(n)

        for lvl in sorted(columns):
            print(f"Level {lvl}")
            for n in columns[lvl]:
                if n.parent:
                    srcs = ", ".join(p.result for p in n.parent)
                    print(f"  [{n.id}] {n.result} = {n.op}({srcs})")
                else:
                    print(f"  [{n.id}] {n.op} {n.result}")

    def _print_tree(self, node, prefix="", is_last=True, is_root=True):
        label = f"{node.result} = {node.op}" if node.parent else str(node.result)

        if is_root:
            print(label)
            child_prefix = ""
        else:
            print(prefix + ("└── " if is_last else "├── ") + label)
            child_prefix = prefix + ("    " if is_last else "│   ")

        for i, p in enumerate(node.parent):
            self._print_tree(p, child_prefix, i == len(node.parent) - 1, False)

    def print_tree(self):
        # one tree per output (a node nothing else uses)
        for n in self.nodes:
            if not n.child:
                self._print_tree(n)
                print()