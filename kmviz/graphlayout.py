import math
import networkx as nx
import numpy as np

def layout(graph, fixed):
    k = 0.10
    
    pos = fruchterman_reingold_layout(graph, pos=fixed, fixed=fixed.keys(), k=k, iterations=500)
    base_score = scoring(graph, pos)
    print base_score
    
    for a in graph.nodes():
        if a in fixed:
            continue
        if len(graph.neighbors(a)) == 0:
            for i in range(10):
                for i in range(10):
                    score = 0
                    delta = np.zeros(2)
                    pos[a][pos[a] < 0] = 0
                    pos[a][pos[a] > 1] = 1
                    for b in graph.nodes():
                        diff = pos[a] - pos[b]
                        dist2 = sum(diff**2)            
                        if dist2 < 0.0625:
                            score += 0.0625 - dist2
                            delta += (0.0625 - dist2) * diff
                    if sum(delta) == 0:
                        break
                    pos[a] += delta
                if sum(delta) == 0:
                    break
                pos[a] = np.random.uniform(size=2)
        else:
            for b in graph.neighbors(a):
                if b in fixed:
                    continue
                new_pos = dict((a, (pos[a][0], pos[a][1])) for a in pos)
                new_pos[b], new_pos[a] = new_pos[a], new_pos[b]
                new_pos = fruchterman_reingold_layout(graph, pos=new_pos, fixed=fixed.keys(), k=k)
                new_score = scoring(graph, new_pos)
                if new_score < base_score:
                    pos = new_pos
                    base_score = new_score
                    print "flipped %s and %s (score now %.2f)" % (a, b, base_score)
    
    return pos

def scoring(graph, pos):
    score = 0.0
    for a in graph.nodes():
        for b in graph.nodes():
            dist2 = sum((pos[a] - pos[b])*(pos[a] - pos[b]))
            
            if graph.has_edge(a, b):
                if dist2 > 0.0625:
                    score += dist2 - 0.0625
            else:
                if dist2 < 0.0625:
                    score += 0.0625 - dist2

    return score


def fruchterman_reingold_layout(G,dim=2,k=None,
                                pos=None,
                                fixed=None,
                                iterations=50,
                                weight='weight',
                                scale=1.0):
    """Position nodes using Fruchterman-Reingold force-directed algorithm.
    Parameters
    ----------
    G : NetworkX graph or list of nodes
    dim : int
       Dimension of layout
    k : float (default=None)
       Optimal distance between nodes.  If None the distance is set to
       1/sqrt(n) where n is the number of nodes.  Increase this value
       to move nodes farther apart.
    pos : dict or None  optional (default=None)
       Initial positions for nodes as a dictionary with node as keys
       and values as a list or tuple.  If None, then use random initial
       positions.
    fixed : list or None  optional (default=None)
      Nodes to keep fixed at initial position.
    iterations : int  optional (default=50)
       Number of iterations of spring-force relaxation
    weight : string or None   optional (default='weight')
        The edge attribute that holds the numerical value used for
        the edge weight.  If None, then all edge weights are 1.
    scale : float (default=1.0)
        Scale factor for positions. The nodes are positioned
        in a box of size [0,scale] x [0,scale].
    center : array-like or None
       Coordinate pair around which to center the layout.
    Returns
    -------
    dict :
       A dictionary of positions keyed by node
    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> pos=nx.spring_layout(G)
    # The same using longer function name
    >>> pos=nx.fruchterman_reingold_layout(G)
    """
    if fixed is None:
        fixed = []
        
    nfixed = dict(zip(G, range(len(G))))
    fixed = np.asarray([nfixed[v] for v in fixed])

    shape = (len(G), dim)
    pos_arr = np.random.uniform(low=0, high=scale, size=shape)
    try:
        for i, n in enumerate(G):
            if n in pos:
                pos_arr[i] = np.asarray(pos[n])
    except TypeError:
        pass

    if len(G) == 0:
        return {}
    if len(G) == 1:
        return {G.nodes()[0]: pos_arr[0]}

    A = nx.to_numpy_matrix(G, weight=weight)
    if k is None and fixed is not None:
       # We must adjust k by domain size for layouts that are not near 1x1
       nnodes,_ = A.shape
       k = scale / np.sqrt(nnodes)
    pos = _fruchterman_reingold(A, dim, k, pos_arr, fixed, iterations)
    return dict(zip(G,pos))

def _fruchterman_reingold(A, dim, k, pos, fixed, iterations):

    A=np.asarray(A) # make sure we have an array instead of a matrix
    pos = np.asarray(pos)

    # make sure positions are of same type as matrix

    # the initial "temperature"  is about .1 of domain area (=1x1)
    # this is the largest step allowed in the dynamics.
    # We need to calculate this in case our fixed positions force our domain
    # to be much bigger than 1x1
    t = max(max(pos.T[0]) - min(pos.T[0]), max(pos.T[1]) - min(pos.T[1]))*0.1
    # simple cooling scheme.
    # linearly step down by dt on each iteration so last iteration is size dt.
    dt = t / float(iterations + 1)
    delta = np.empty((pos.shape[0], pos.shape[0], pos.shape[1]), dtype = A.dtype)
    # the inscrutable (but fast) version
    # this is still O(V^2)
    # could use multilevel methods to speed this up significantly
    for iteration in range(iterations):
        pos[pos < 0] += 0.05
        pos[pos > 1] -= 0.05
        # matrix of difference between points
        for i in range(pos.shape[1]):
            delta[:, :, i] = pos[:, i, None] - pos[:, i]
        # distance between points
        distance = np.sqrt((delta ** 2).sum(axis=-1))
        # enforce minimum distance of 0.01
        invdistance = k / np.where(distance < 0.01, 0.01, distance)
        # displacement "force"
        displacement = (np.transpose(np.transpose(delta)
                        * (invdistance**2 - A / invdistance))
                        .sum(axis=1))
        # update positions
        length = np.sqrt((displacement**2).sum(axis=1))
        length = np.where(length < 0.01, 0.1, length)
        delta_pos = np.transpose(np.transpose(displacement)*t/length)
        if fixed is not None:
            # don't change positions of fixed nodes
            delta_pos[fixed]=0.0
        pos += delta_pos
        # cool temperature
        t -= dt

    return pos