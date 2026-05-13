# %%
import pandas as pd
import plotly.graph_objects as go

# Read CSV
df = pd.read_csv("data/wiki_sub_category.csv")
# wiki_scrape/data/wiki_sub_category.csv
# Build tree structure
nodes = {}
for _, row in df.iterrows():
    nodes[row["pageid"]] = {
        "title": row["title"],
        "parent": row["parent_id"],
        "depth": row["depth"],
    }

# Create positions
positions = {}
depth_counts = {}

for pid in sorted(nodes.keys(), key=lambda x: nodes[x]["depth"]):
    d = nodes[pid]["depth"]
    depth_counts[d] = depth_counts.get(d, 0) + 1
    positions[pid] = (d, depth_counts[d])

# Prepare edges
edge_x, edge_y = [], []
for pid, node in nodes.items():
    if node["parent"] in positions:
        x0, y0 = positions[node["parent"]]
        x1, y1 = positions[pid]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

# Prepare nodes
node_x = [positions[pid][0] for pid in nodes.keys()]
node_y = [positions[pid][1] for pid in nodes.keys()]
node_text = [nodes[pid]["title"] for pid in nodes.keys()]
# %%
# Plot
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(color="#888", width=0.5),
        hoverinfo="none",
        showlegend=False,
    )
)

fig.add_trace(
    go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        marker=dict(size=8, color="lightblue"),
        text=node_text,
        textposition="top center",
        hoverinfo="text",
        showlegend=False,
    )
)

fig.update_layout(
    title="Tree Structure",
    xaxis=dict(title="Depth", showgrid=False),
    yaxis=dict(title="Position", showgrid=False),
    hovermode="closest",
)

fig.show()

# %%
import pandas as pd

# Read CSV
df = pd.read_csv("data/wiki_sub_category.csv")

# Ensure pageid and parent are integers (handle any NaN or string issues)
df["pageid"] = pd.to_numeric(df["pageid"], errors="coerce").astype(
    "Int64"
)  # Int64 handles NaN
df["parent"] = pd.to_numeric(df["parent"], errors="coerce").astype("Int64")

# Remove duplicate rows based on pageid (keep first occurrence)
df_clean = df.drop_duplicates(subset=["pageid"], keep="first")

# Verify: check for remaining duplicates
print(f"Original rows: {len(df)}")
print(f"Cleaned rows: {len(df_clean)}")
print(f"Duplicates removed: {len(df) - len(df_clean)}")
print("Remaining pageid duplicates:", df_clean["pageid"].duplicated().sum())

# Rewrite to same file (overwrites original)
df_clean.to_csv("data/wiki_sub_category.csv", index=False)
print("Cleaned CSV saved: wiki_sub_category.csv")


from treelib import Tree
import csv

tree = Tree()

with open("data/wiki_sub_category.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["parent"] == "":  # ルートノード
            tree.create_node(row["title"], row["pageid"])
        else:
            tree.create_node(row["title"], row["pageid"], parent=row["parent"])

tree.show()  # ツリー全体を表示
