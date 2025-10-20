import pandas as pd
import networkx as nx
import ast

def build_graph(df, include_replies=True, include_quotes=True):
    G = nx.DiGraph()
    for _, row in df.iterrows():
        author = row["user"]

        # Handle replying-to (list)
        replying_to = []
        if pd.notna(row["replying-to"]):
            try:
                replying_to = ast.literal_eval(row["replying-to"])
            except:
                pass

        if include_replies:
            for target in replying_to:
                G.add_edge(author, target, interaction="reply")

        # Handle quoting
        quoted = row.get("quoting")
        if include_quotes and pd.notna(quoted) and quoted != "":
            G.add_edge(author, quoted, interaction="quote")

    # Node centrality for size
    centrality = nx.degree_centrality(G)
    for n in G.nodes():
        G.nodes[n]["centrality"] = centrality.get(n, 0)

    return G

# --------------------------------------------------
# 3. Convert to Cytoscape format
# --------------------------------------------------
def nx_to_cyto(G):
    elements = []
    for n, data in G.nodes(data=True):
        elements.append({
            "data": {
                "id": n,
                "label": n,
                "centrality": round(data.get("centrality", 0), 4),
            }
        })
    for u, v, data in G.edges(data=True):
        elements.append({
            "data": {
                "source": u,
                "target": v,
                "interaction": data.get("interaction", "unknown")
            }
        })
    return elements