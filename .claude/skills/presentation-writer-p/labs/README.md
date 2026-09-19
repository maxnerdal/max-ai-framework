# Lab-referenser för TDDD95 / ETE389

Källa: https://www.ida.liu.se/~TDDD95/timetable/index.en.shtml

Varje lab-nummer på timetable-sidan är länkad till en extern resurs (cp-algorithms.com,
geeksforgeeks.org, eller topcoder.com) som innehåller förklaring och kod-exempel. Detta
är den kod Max faktiskt läser när hen jobbar med respektive problem — vilket gör dem
till primära källor för process-berättelsen i Presentation-Answers.md.

## URL-mappning

| Lab | Topic | URL | Sparad lokalt |
|-----|-------|-----|---------------|
| 1.1 | Intro to Greedy and DP | https://medium.com/cracking-the-data-science-interview/greedy-algorithm-and-dynamic-programming-a8c019928405 | nej |
| 1.2 | Knapsack Problem | https://www.geeksforgeeks.org/0-1-knapsack-problem-dp-10/ | nej |
| 1.3 | Longest Increasing Subsequence | https://www.codechef.com/wiki/tutorial-dynamic-programming | nej |
| 1.4 | Union-Find | https://cp-algorithms.com/data_structures/disjoint_set_union.html | nej |
| 1.5 | Fenwick Tree | https://cp-algorithms.com/data_structures/fenwick.html | nej |
| 1.6 | Fast Fourier Transform | https://cp-algorithms.com/algebra/fft.html | nej |
| 1.7 | Gaussian Elimination | https://cp-algorithms.com/linear_algebra/linear-system-gauss.html | nej |
| **2.1** | **Dijkstra Shortest Path** | https://cp-algorithms.com/graph/dijkstra.html | nej |
| **2.2** | **Dijkstra Shortest Path** | https://cp-algorithms.com/graph/dijkstra.html | nej (samma som 2.1) |
| **2.3** | **Bellman-Ford Algorithm** | https://cp-algorithms.com/graph/bellman_ford.html | nej |
| **2.4** | **Floyd-Warshall All-Pairs** | https://cp-algorithms.com/graph/all-pair-shortest-path-floyd-warshall.html | nej |
| **2.5** | **Kruskal's MST** | https://cp-algorithms.com/graph/mst_kruskal.html | nej |
| **2.6** | **Maximum Flow** | https://cp-algorithms.com/graph/edmonds_karp.html | ✅ `lab-2.6-cpp.md` |
| **2.7** | **Minimum Cut** | https://www.geeksforgeeks.org/minimum-cut-in-a-directed-graph/ | ✅ `lab-2.7-python.md` |
| **2.8** | **Min Cost Max Flow** | https://www.topcoder.com/community/data-science/data-science-tutorials/minimum-cost-flow-part-one-key-concepts/ | nej |
| **2.9** | **Euler Path** | https://cp-algorithms.com/graph/euler_path.html | nej |
| 3.1 | Knuth-Morris-Pratt | https://cp-algorithms.com/string/prefix-function.html | nej |

## Vilka labbar är relevanta för vilka problem?

| Problem | Relevanta labbar | Rationale |
|---------|------------------|-----------|
| mincut | 2.6, 2.7 | max-flow + min-cut extraktion |
| paintball | (matching, ej i tabellen) | bipartit matchning via Hopcroft-Karp — utanför labbtabellen |
| RA duty scheduler | 2.6 | max-flow med binärsökning |
| kingofthenorth | 2.6, 2.7 | min-cut med node-splitting |
| shortestpath1 | 2.1, 2.2 | Dijkstra |
| minspantree | 2.5 | Kruskal MST |
| blockcrusher | 2.1 | Dijkstra på rutnät |
| tidegoesin | 2.1 | Dijkstra med tids­beroende |

## Strategi

**Hämta on-demand:** när vi börjar jobba med ett nytt problem, kör WebFetch på
respektive lab-URL och spara innehållet som `labs/lab-2.X-{language}.md` med:
- Grafrepresentation
- Algoritm som visas
- Komplexitet
- Full kod
- Eventuella nyckel-observationer som skiljer sig från CP4 eller Max faktiska kod

Detta säkerställer att jag alltid har full koll på vad Max faktiskt kunde läsa på
lab-nivån innan jag skriver om ett problem.
