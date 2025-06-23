---
title: Full Intertext Diagram
---

# Full Intertext Diagram

The following diagram shows the connections between all intertexts currently in the database.

Each rectangular node represents one section of a work (a `work segment`, as defined on <a href="./about#database-design">the About page</a>). A flow path linking two nodes represents words that have been identified as intertexts between the source text (higher up) and the target text (lower down); its width shows (in relative terms) *how many* words are borrowed.

Mouse over a node to see the work and section that it represents. Mouse over a linking flow path to see the words it represents.

<div style="font-size:smaller;">

A subset of this diagram is shown on the main page for the currently-selected portion of a work.

*Some additional future work:*
- *making the nodes repositionable*
- *highlighting the entire set of flows connected to the currently-selected node*

</div>
<hr>

<div>

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
    nodeGroup: d => d.author,
    nodeLabel: d => {
        //chartNodes.push(d);
                    let nodesFilter = nodes.filter(node => node.id === d.id);
                    let nodeAuthorID;
                    for (let n in nodesFilter) {nodeAuthorID = nodesFilter[n].author}
                    return lookupIDTable.get(nodeAuthorID);
                    },
    nodeTitle: d => `${lookupIDTable.get(d.id).work}\n${lookupIDTable.get(d.id).section}`,
    nodeSort: (a,b) => {
        let nodeA = sankeyData.nodes.find(work => work.name === a.id);
        let nodeB = sankeyData.nodes.find(work => work.name === b.id);
        // Sort so that authors go A-Z left-to-right (= bottom-to-top)
        let authorComp = d3.descending(lookupIDTable.get(nodeA.author), lookupIDTable.get(nodeB.author));
        if (authorComp !== 0) return authorComp; // if the authors aren't the same, don't go any further in sorting
        // Within authors, sort so that all work sections are in order by work
        // eventually may sort additionally by work section
        return d3.descending(lookupIDTable.get(nodeA.work), lookupIDTable.get(nodeB.work));
    },
    align: "center",
    //colors: d3.schemeSpectral[11], // should be able to create a bigger range by bringing colorcet colors in via Python
    colors: authorColors,
    linkColor: "source",
    // linkTitle: d => {
    //     //chartLinks.push(d);
    //     let sourceNode = d.source.id;
    //     let targetNode = d.target.id;
    //     let linkSet = sankeyData.edges.filter(l => l.source === sourceNode && l.target === targetNode);
    //     // let nodesFilterSource = nodes.filter(n => n.id === d.source.id);
    //     // let sourceWordIDs = [];
    //     let sourceWordIDs = [];
    //     let targetWordIDs = [];
    //     for (let i in linkSet) {
    //         linkSet[i].source_words.map(w => sourceWordIDs.push(w));
    //         linkSet[i].target_words.map(w => targetWordIDs.push(w));
    //     }

    //     sourceWordIDs = [...new Set(sourceWordIDs)];
    //     targetWordIDs = [...new Set(targetWordIDs)];

    //     let sourceWords = [];
    //     let targetWords = [];

    //     for (let i in sourceWordIDs) {sourceWords.push(lookupIDTable.get(sourceWordIDs[i]));}
    //     sourceWords.sort((a,b) => {
    //         if (a.lineNum < b.lineNum) {
    //             return -1
    //         } else if (a.lineNum > b.lineNum) {
    //             return 1
    //         } else {return 0}
    //     })
    //     for (let i in sourceWords) {sourceWords[i] = `${sourceWords[i].word} (line ${sourceWords[i].lineNum})`}
        
    //     for (let i in targetWordIDs) {targetWords.push(lookupIDTable.get(targetWordIDs[i]));}
    //     targetWords.sort((a,b) => {
    //         if (a.lineNum < b.lineNum) {
    //             return -1
    //         } else if (a.lineNum > b.lineNum) {
    //             return 1
    //         } else {return 0}
    //     })
    //     for (let i in targetWords) {targetWords[i] = `${targetWords[i].word} (line ${targetWords[i].lineNum})`}

    //     return `${lookupIDTable.get(sourceNode).work}, ${lookupIDTable.get(sourceNode).section}: ${sourceWords.join(', ')}\n${lookupIDTable.get(targetNode).work}, ${lookupIDTable.get(targetNode).section}: ${targetWords.join(', ')}`;
    // }
    linkTitle: null
})

```

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
import {createLookupIDTable, authorColors} from './js/global_constants.js';
import {SankeyChart} from './js/sankey_function.js';
```

```js
// Create mapping of ID-to-name
const lookupIDTable = createLookupIDTable(nodegoatTables);
```

<!-- End import modules and constants -->
