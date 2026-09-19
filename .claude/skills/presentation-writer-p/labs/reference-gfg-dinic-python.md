# GeeksforGeeks — Dinic's Algorithm for Maximum Flow (Python)

**URL:** https://www.geeksforgeeks.org/dsa/dinics-algorithm-maximum-flow/

**INTE en officiell lab-länk** i TDDD95 (Lab 2.7 pekar på GfG:s min-cut-sida, en annan
GfG-artikel). Men denna sida är en trolig källa för Max grafrepresentation i
`mincut.py`, eftersom `len(graph[v])` som rev_index-mönster matchar exakt.

## Karaktäristika

- **Grafrepresentation:** Adjacency list med `Edge`-klass som har `.v`, `.flow`, `.C`, `.rev`.
- **Algoritm:** Dinic (till skillnad från Lab 2.7 som är Edmonds-Karp).
- **Bakåtkant:** explicit, med `flow=0, C=0`.
- **rev_index:** beräknas med `len(self.adj[v])` när kanten skapas.

## Nyckel-överensstämmelse med Max mincut.py

**GfG:**
```python
def addEdge(self, u, v, C):
    a = Edge(v, 0, C, len(self.adj[v]))    # framåt: rev = där bakåtkanten ska hamna
    b = Edge(u, 0, 0, len(self.adj[u]))    # bakåt: rev = där framåtkanten ska hamna
    self.adj[u].append(a)
    self.adj[v].append(b)
```

**Max (`mincut.py` rad 16–18):**
```python
def add_edge(u, v, cap):
    graph[u].append([v, cap, len(graph[v])])       # framåt: rev = där bakåtkanten ska hamna
    graph[v].append([u, 0, len(graph[u]) - 1])     # bakåt: rev = där framåtkanten hamnade
```

Samma idé, bara med list `[to, cap, rev_index]` istället för Edge-klass, och `-1`
i bakåtkanten (eftersom framåtkanten just appendats).

## Fullkod

```python
# Python implementation of Dinic's Algorithm
class Edge:
    def __init__(self, v, flow, C, rev):
        self.v = v
        self.flow = flow
        self.C = C
        self.rev = rev

# Residual Graph
class Graph:
    def __init__(self, V):
        self.adj = [[] for i in range(V)]
        self.V = V
        self.level = [0 for i in range(V)]

    # add edge to the graph
    def addEdge(self, u, v, C):
        # Forward edge : 0 flow and C capacity
        a = Edge(v, 0, C, len(self.adj[v]))
        # Back edge : 0 flow and 0 capacity
        b = Edge(u, 0, 0, len(self.adj[u]))
        self.adj[u].append(a)
        self.adj[v].append(b)

    # Finds if more flow can be sent from s to t
    # Also assigns levels to nodes
    def BFS(self, s, t):
        for i in range(self.V):
            self.level[i] = -1
        # Level of source vertex
        self.level[s] = 0
        # Create a queue, enqueue source vertex
        q = []
        q.append(s)
        while q:
            u = q.pop(0)
            for i in range(len(self.adj[u])):
                e = self.adj[u][i]
                if self.level[e.v] < 0 and e.flow < e.C:
                    self.level[e.v] = self.level[u]+1
                    q.append(e.v)
        return False if self.level[t] < 0 else True

    # A DFS based function to send flow after BFS has
    # figured out that there is a possible flow and
    # constructed levels. This functions called multiple
    # times for a single call of BFS.
    def sendFlow(self, u, flow, t, start):
        # Sink reached
        if u == t:
            return flow
        # Traverse all adjacent edges one -by -one
        while start[u] < len(self.adj[u]):
            e = self.adj[u][start[u]]
            if self.level[e.v] == self.level[u]+1 and e.flow < e.C:
                curr_flow = min(flow, e.C-e.flow)
                temp_flow = self.sendFlow(e.v, curr_flow, t, start)
                if temp_flow and temp_flow > 0:
                    e.flow += temp_flow
                    self.adj[e.v][e.rev].flow -= temp_flow
                    return temp_flow
            start[u] += 1

    # Returns maximum flow in graph
    def DinicMaxflow(self, s, t):
        # Corner case
        if s == t:
            return -1
        total = 0
        # Augument the flow while there is path
        while self.BFS(s, t) == True:
            start = [0 for i in range(self.V+1)]
            while True:
                flow = self.sendFlow(s, float('inf'), t, start)
                if not flow:
                    break
                total += flow
        return total

g = Graph(6)
g.addEdge(0, 1, 16)
g.addEdge(0, 2, 13)
g.addEdge(1, 2, 10)
g.addEdge(1, 3, 12)
g.addEdge(2, 1, 4)
g.addEdge(2, 4, 14)
g.addEdge(3, 2, 9)
g.addEdge(3, 5, 20)
g.addEdge(4, 3, 7)
g.addEdge(4, 5, 4)

print("Maximum flow", g.DinicMaxflow(0, 5))

# This code is contributed by rupasriachanta421.
```
