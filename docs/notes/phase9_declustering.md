# Phase 9: Declustering & Probabilistic Genealogy

## 1. Deterministic vs. Stochastic Declustering
**Deterministic (Window) Declustering:** Traditional methods like Gardner & Knopoff (1974) draw a deterministic time-and-space cylinder around every earthquake based on its magnitude. Any subsequent earthquake falling inside that cylinder is rigidly classified as an aftershock and deleted from the catalog. While simple, this creates hard, unnatural boundaries, deletes independent background events that happen to fall inside the cylinder, and physically breaks the scaling laws of natural seismicity.

**Probabilistic (Stochastic) Declustering:** In the ETAS framework (Zhuang et al. 2002), we don't assign rigid 1 or 0 labels. Instead, we use the fitted model to compute the exact probability $bg_i$ that event $i$ is a background event, and $\rho_{ij}$ that event $j$ triggered event $i$. 
We then *stochastically* sample a uniform random number $U \in [0, 1]$. If $U < bg_i$, event $i$ is kept as a background event. By repeating this process across multiple realizations, we get a true probabilistic distribution of the declustered catalog without violating physical scaling laws.

## 2. The Triggering Graph
The probabilistic matrix $\rho_{ij}$ naturally forms a directed acyclic graph (DAG):
- **Nodes:** Every earthquake in the catalog.
- **Edges:** A directed edge from parent $j$ to offspring $i$, with a weight equal to $\rho_{ij}$.
- **Background Nodes:** Nodes where the sum of incoming edges $\sum_j \rho_{ij} < 1$, with the remaining probability $bg_i$ representing the edge weight from an invisible "background" root source.

From this graph, we can extract powerful network features for downstream machine learning:
1. **Expected Offspring:** The out-degree of node $j$, computed as $\sum_i \rho_{ij}$.
2. **Generation Depth:** How deep into an aftershock cascade an event is (background = 0, direct aftershock = 1, secondary = 2).
3. **Cluster Size:** The total expected number of descendants (direct and indirect) branching from a single background event.
