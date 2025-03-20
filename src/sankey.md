---
title: Full Intertext Diagram
---

Mouse over a rectangular node to see the work and section that it represents. Mouse over a linking flow path to see the words it represents.

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
     value: edge.num_words
   });
 }
```

```js
const chart = SankeyChart({nodes: nodes, links: links},
{
    nodeGroup: d => d.author,
    nodeLabel: d => {let nodesFilter = nodes.filter(node => node.id === d.id);
                    let nodeAuthorID;
                    for (let n in nodesFilter) {nodeAuthorID = nodesFilter[n].author}
                    return lookupIDTable.get(nodeAuthorID);
                    },
    nodeTitle: d => `${lookupIDTable.get(d.id).work}\n${lookupIDTable.get(d.id).section}`,
    align: "center",
    linkColor: "source",
    linkTitle: d => {
        let sourceNode = d.source.id;
        let targetNode = d.target.id;
        let linkSet = sankeyData.edges.filter(l => l.source === sourceNode && l.target === targetNode);
        // let nodesFilterSource = nodes.filter(n => n.id === d.source.id);
        // let sourceWordIDs = [];
        let sourceWordIDs = [];
        let targetWordIDs = [];
        for (let i in linkSet) {
            linkSet[i].source_words.map(w => sourceWordIDs.push(w));
            linkSet[i].target_words.map(w => targetWordIDs.push(w));
        }
        let sourceWords = [];
        let targetWords = [];

        for (let i in sourceWordIDs) {sourceWords.push(lookupIDTable.get(sourceWordIDs[i]));}
        sourceWords.sort((a,b) => {
            if (a.lineNum < b.lineNum) {
                return -1
            } else if (a.lineNum > b.lineNum) {
                return 1
            } else {return 0}
        })
        for (let i in sourceWords) {sourceWords[i] = `${sourceWords[i].word} (line ${sourceWords[i].lineNum})`}
        
        for (let i in targetWordIDs) {targetWords.push(lookupIDTable.get(targetWordIDs[i]));}
        targetWords.sort((a,b) => {
            if (a.lineNum < b.lineNum) {
                return -1
            } else if (a.lineNum > b.lineNum) {
                return 1
            } else {return 0}
        })
        for (let i in targetWords) {targetWords[i] = `${targetWords[i].word} (line ${targetWords[i].lineNum})`}

        return `${lookupIDTable.get(sourceNode).work}: ${sourceWords.join(', ')}\n${lookupIDTable.get(targetNode).work}: ${targetWords.join(', ')}`;
    }
})


view(chart)
```

Eventually, subsets of this diagram will appear on the main page for the currently-selected portion of a work.

<!-- LOAD DATA, ETC. BELOW THIS LINE -->

```js
import {SankeyChart} from "./components/sankey.js";
```

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

<!-- Create mapping of ID-to-name -->
```js
const lookupIDTable = new Map();

for (let i in nodegoatTables.word_instance_table) {
	let item = nodegoatTables.word_instance_table[i];
	let key = item.obj_id;
	let word = item.word;
	let line = item.line_num;
	let def = {'word': word, 'lineNum': line};
	lookupIDTable.set(key, def);
}

for (let i in nodegoatTables.author_table) {
	let item = nodegoatTables.author_table[i];
	let key = item.obj_id;
	let def = item.author_name;
	lookupIDTable.set(key, def);
}

// I may want to change this to a dictionary that includes author as well as title
for (let i in nodegoatTables.work_table) {
	let item = nodegoatTables.work_table[i];
	let key = item.obj_id;
	let def = item.title;
	lookupIDTable.set(key, def);
}
```
```js
for (let i in nodegoatTables.work_seg_table) {
	let item = nodegoatTables.work_seg_table[i];
	let section = item.work_section || '';
	let subsec = item.work_subsection || '';
	let key = item.obj_id;
	let work_id = String(item.work_id);
	let work = lookupIDTable.get(work_id);
	let section_string;
	if (section && subsec) {
		section_string = `${section}, ${subsec}`;
	} else if (section) {
		section_string = `${section}`;
	} else {
		section_string = '';
	}
	let def = {'work': work, 'section': section_string};
	lookupIDTable.set(key, def);
}
```
<!-- End mapping -->

