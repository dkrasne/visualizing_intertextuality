---
title: Full Intertext Diagram
theme: [wide, air]
toc: false
---

# Full Intertext Diagram

The diagram on this page shows the connections between all intertexts currently in the database; a subset of this diagram is shown on the main page for the selected portion of a work.

Each rectangular node represents one section of a work (a `work segment`, as defined on [the About page](./about#database-design)). A flow path linking two nodes represents words that have been identified as intertexts between the source text (the higher node) and the target text (the lower node); its width shows (in relative terms) *how many* words are borrowed.

## How to use this visualization

Mouse over a node to see the work and section that it represents. Mouse over a linking flow path to see the words it represents. (N.B. If the link you want to see information for is covered by other links, you can mouse over either of the two nodes attached to it in order to raise it to the surface.)

Tick the following box to sort the nodes (within a given row) alphabetically by author and work; authors may still appear in multiple rows. If you leave the box **unticked**, the nodes will be placed in their optimal position as determined by the connections between them (which makes the overall diagram less messy but also potentially less intuitive).

```js
const authorSort = view(Inputs.toggle({label: html`Sort nodes by author?`}));
```


<hr>

<div style="max-width: none;">

```js
display(chart)
```

</div>

```js
const nodes = [];
  
for (let node in sankeyData.nodes) {
  let nodeString = String(node)
  nodes.push({
    id: sankeyData.nodes[node].name,
    author: sankeyData.nodes[node].author,
    work: sankeyData.nodes[node].work
  });
}
```

```js
const links = [];

 for (let i in sankeyData.edges) {
   let edge = sankeyData.edges[i];

   links.push({
     source: edge.source,
     target: edge.target,
     value: edge.num_words,
	 source_words: edge.source_words,
	 target_words: edge.target_words
   });
 }
```

```js
// const chartNodes = [];
// const chartLinks = [];
// const chartData = {nodes: chartNodes, links: chartLinks}

const chart = SankeyChart({nodes: nodes, links: links, lookupIDTable: lookupIDTable},
{
    nodeGroup: d => {
        if (!d.author) {return lookupIDTable.get(d.id).workID} // this should enable coloring of anonymous works by the work itself
        return d.author
      },
    nodeLabel: d => {
        //chartNodes.push(d);
        let nodesFilter = nodes.filter(node => node.id === d.id);
        let nodeAuthorID;
        for (let n in nodesFilter) {nodeAuthorID = nodesFilter[n].author}
        return lookupIDTable.get(nodeAuthorID);
      },
    nodeTitle: null,
    nodeSort: !authorSort ? 
      undefined : 
      function(a,b) {
				let nodeA = sankeyData.nodes.find(work => work.name === a.id);
				let nodeB = sankeyData.nodes.find(work => work.name === b.id);
				// Sort so that authors go A-Z left-to-right (= bottom-to-top); d3.descending returns -1, 0, or 1
        // anonymous works should be ordered under "anonymous" plus their title
        let authorA = nodeA.author ? lookupIDTable.get(nodeA.author) : "anonymous";
        let authorB = nodeB.author ? lookupIDTable.get(nodeB.author) : "anonymous";
        if (authorA === "anonymous") {
					authorA += d3.descending(lookupIDTable.get(nodeA.work).workTitle)
				}
				if (authorB === "anonymous") {
					authorB += d3.descending(lookupIDTable.get(nodeB.work).workTitle)
				}
				let authorComp = d3.descending(authorA.toLowerCase(), authorB.toLowerCase()); // d3 sort is case sensitive
				// Within authors, sort so that all work sections are in order by work
				let workComp = d3.descending(lookupIDTable.get(nodeA.work).workTitle, lookupIDTable.get(nodeB.work).workTitle);
        let workSegComp = lookupIDTable.get(b.id).section.localeCompare(lookupIDTable.get(a.id).section, undefined, {numeric:true});
				if (authorComp !== 0) return authorComp; // if the authors aren't the same, don't go any further in sorting
				if (workComp !== 0) return workComp;
				return workSegComp; // sort by work section
      },
    align: "center",
    //colors: d3.schemeSpectral[11], // should be able to create a bigger range by bringing colorcet colors in via Python
    colors: authorColors,
    linkColor: "source",
    height: 750,
    width: 1000,
    linkTitle: null
})

```

<hr>

<div style="font-size:smaller;">

*Some additional future work:*
- *making the nodes repositionable*
- *filtering to only show selected author(s) and work(s)* <!-- use Inputs.table() to assist with this. https://observablehq.com/framework/inputs/table -->

</div>


<hr>

Anything below here will not appear in the final version.

```js
chart.nodes
```
```js
chart.links
```

<!-- LOAD DATA, ETC. BELOW THIS LINE -->

<!-- Load data -->

```js
// Attach extracted nodegoat objects (final output of Python data loader)
const nodegoatModel = FileAttachment("data/nodegoat_data.json").json()
```
```js
// Attach restructured tables for querying
const nodegoatTables = FileAttachment("data/nodegoat_tables.json").json()
```
```js
// Attach meters table for querying.
const meters = FileAttachment("data/meters.json").json()
```
```js
// Attach full list of intertexts (used for network)
const intertextsTable = FileAttachment("data/intxts_full.json").json()
```
```js
// Attach networkx graph json
const graphData = FileAttachment("data/intxt_network_graph.json").json()
```
```js
// Attach sankey chart data
const sankeyData = FileAttachment("data/sankey_data.json").json()
```
<!-- End load data -->


<!-- Import modules and constants -->

```js
import {createLookupIDTable, nodeSortAuthor, authorColors} from './js/global_constants.js';
import {SankeyChart} from './js/sankey_function.js';
```

```js
// Create mapping of ID-to-name
const lookupIDTable = createLookupIDTable(nodegoatTables);
```

<!-- End import modules and constants -->
