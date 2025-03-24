---
title: Full Intertext Diagram
---

# Full Intertext Diagram

The following diagram shows the connections between all intertexts currently in the database.

Each node represents one section of a work (a `work segment`, as defined on <a href="./about#database-design">the About page</a>). A flow path linking two nodes represents words that have been identified as intertexts between the source text (higher up) and the target text (lower down); its width shows (in relative terms) *how many* words are borrowed.

Mouse over a rectangular node to see the work and section that it represents. Mouse over a linking flow path to see the words it represents. (Currently, the latter may not work on mobile phones.)

<div style="font-size:smaller;">

Eventually, subsets of this diagram will appear on the main page for the currently-selected portion of a work.

*Some possible additional future work:*
- *making the nodes repositionable*
- *highlighting the entire set of flows connected to the currently-selected node*

</div>
<hr>

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
// const chartNodes = [];
// const chartLinks = [];
// const chartData = {nodes: chartNodes, links: chartLinks}

const chart = SankeyChart({nodes: nodes, links: links},
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
    align: "center",
    linkColor: "source",
    linkTitle: d => {
        //chartLinks.push(d);
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

        sourceWordIDs = [...new Set(sourceWordIDs)];
        targetWordIDs = [...new Set(targetWordIDs)];

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

        return `${lookupIDTable.get(sourceNode).work}, ${lookupIDTable.get(sourceNode).section}: ${sourceWords.join(', ')}\n${lookupIDTable.get(targetNode).work}, ${lookupIDTable.get(targetNode).section}: ${targetWords.join(', ')}`;
    }
})


view(chart)
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



```js
//create customized SankeyChart() function
// ORIGINAL VERSION:
// Copyright 2021-2023 Observable, Inc.
// Released under the ISC license.
// https://observablehq.com/@d3/sankey-diagram


import * as d3Sankey from "npm:d3-sankey@0.12.3";

function SankeyChart(
  {
    nodes, // an iterable of node objects (typically [{id}, …]); implied by links if missing
    links // an iterable of link objects (typically [{source, target}, …])
  },
  {
    format = ",", // a function or format specifier for values in titles
    align = "justify", // convenience shorthand for nodeAlign
    nodeId = (d) => d.id, // given d in nodes, returns a unique identifier (string)
    nodeGroup, // given d in nodes, returns an (ordinal) value for color
    nodeGroups, // an array of ordinal values representing the node groups
    nodeLabel, // given d in (computed) nodes, text to label the associated rect
    nodeTitle = (d) => `${d.id}\n${format(d.value)}`, // given d in (computed) nodes, hover text
    nodeAlign = align, // Sankey node alignment strategy: left, right, justify, center
    nodeSort, // comparator function to order nodes
    nodeWidth = 15, // width of node rects
    nodePadding = 10, // vertical separation between adjacent nodes
    nodeLabelPadding = 6, // horizontal separation between node and label
    nodeStroke = "currentColor", // stroke around node rects
    nodeStrokeWidth, // width of stroke around node rects, in pixels
    nodeStrokeOpacity, // opacity of stroke around node rects
    nodeStrokeLinejoin, // line join for stroke around node rects
    linkSource = ({source}) => source, // given d in links, returns a node identifier string
    linkTarget = ({target}) => target, // given d in links, returns a node identifier string
    linkValue = ({value}) => value, // given d in links, returns the quantitative value
    linkPath = d3Sankey.sankeyLinkHorizontal(), // given d in (computed) links, returns the SVG path
    linkTitle = (d) => `${d.source.id} → ${d.target.id}\n${format(d.value)}`, // given d in (computed) links
    linkColor = "source-target", // source, target, source-target, or static color
    linkStrokeOpacity = 0.5, // link stroke opacity
    dark, // using dark mode?
    linkMixBlendMode = dark ? "screen" : "multiply", // link blending mode
    colors = d3.schemeTableau10, // array of colors
    width = 640, // outer width, in pixels
    height = 400, // outer height, in pixels
    marginTop = 5, // top margin, in pixels
    marginRight = 1, // right margin, in pixels
    marginBottom = 5, // bottom margin, in pixels
    marginLeft = 1 // left margin, in pixels
  } = {}
) {
  // Convert nodeAlign from a name to a function (since d3-sankey is not part of core d3).
  if (typeof nodeAlign !== "function")
    nodeAlign =
      {
        left: d3Sankey.sankeyLeft,
        right: d3Sankey.sankeyRight,
        center: d3Sankey.sankeyCenter
      }[nodeAlign] ?? d3Sankey.sankeyJustify;

  // keep original node & link values
  const origNodes = [...nodes];
  const origLinks = [...links];

  // Compute values.
  const LS = d3.map(links, linkSource).map(intern);
  const LT = d3.map(links, linkTarget).map(intern);
  const LV = d3.map(links, linkValue);
  if (nodes === undefined) nodes = Array.from(d3.union(LS, LT), (id) => ({id}));
  const N = d3.map(nodes, nodeId).map(intern);
  const G = nodeGroup == null ? null : d3.map(nodes, nodeGroup).map(intern);

  // Replace the input nodes and links with mutable objects for the simulation.
  nodes = d3.map(nodes, (_, i) => ({id: N[i]}));
  links = d3.map(links, (_, i) => ({source: LS[i], target: LT[i], value: LV[i]}));

  // Ignore a group-based linkColor option if no groups are specified.
  if (!G && ["source", "target", "source-target"].includes(linkColor)) linkColor = "currentColor";

  // Compute default domains.
  if (G && nodeGroups === undefined) nodeGroups = G;

  // Construct the scales.
  const color = nodeGroup == null ? null : d3.scaleOrdinal(nodeGroups, colors);

const browserWidth = window.innerWidth;

  // Compute the Sankey layout.
  d3Sankey
    .sankey()
    .nodeId(({index: i}) => N[i])
    .nodeAlign(nodeAlign)
    .nodeWidth(nodeWidth)
    .nodePadding(nodePadding)
    .nodeSort(nodeSort)
    .iterations(2000)
    .extent([
      [marginLeft, marginTop],
      [width - marginRight, height - marginBottom]
    ])({nodes, links});

  // Compute titles and labels using layout nodes, so as to access aggregate values.
  if (typeof format !== "function") format = d3.format(format);
  const Tl = nodeLabel === undefined ? N : nodeLabel == null ? null : d3.map(nodes, nodeLabel);
  const Tt = nodeTitle == null ? null : d3.map(nodes, nodeTitle);
  const Lt = linkTitle == null ? null : d3.map(links, linkTitle);

  // A unique identifier for clip paths (to avoid conflicts).
  const uid = `O-${Math.random().toString(16).slice(2)}`;

  const svg = d3
    .create("svg")
    .attr("width", width)
    .attr("height", width)
    .attr("viewBox", [0, 0, width, height])
    .attr("style", "max-width: 100%; height: auto; height: intrinsic;")
    .attr("transform", "rotate(90,0,0) translate("+marginTop+",0)")
    //.attr("style","border: 1px solid black")
    ;

  const link = svg
    .append("g")
    .attr("fill", "none")
    .attr("stroke-opacity", linkStrokeOpacity)
    .attr("class","links")
    .selectAll("g")
    .data(links)
const linkPathG = link
    .join("g")
    .attr("class","link")
    .style("mix-blend-mode", linkMixBlendMode);

  const node = svg
    .append("g")
    .attr("stroke", nodeStroke)
    .attr("stroke-width", nodeStrokeWidth)
    .attr("stroke-opacity", nodeStrokeOpacity)
    .attr("stroke-linejoin", nodeStrokeLinejoin)
    .attr("class","nodes")
    .selectAll("g")
    .data(nodes)
    .join("g")
    .attr("class","node")
;

    const nodeRect = node
        .append("rect")
        .attr("x", (d) => d.x0)
        .attr("y", (d) => d.y0)
        .attr("height", (d) => d.y1 - d.y0)
        .attr("width", (d) => d.x1 - d.x0)
        .attr("opacity","0.6");


  if (G) node.attr("fill", ({index: i}) => color(G[i]));
//  if (Tt) node.append("title").text(({index: i}) => Tt[i]);

  if (linkColor === "source-target")
    linkPathG
      .append("linearGradient")
      .attr("id", (d) => `${uid}-link-${d.index}`)
      .attr("gradientUnits", "userSpaceOnUse")
      .attr("x1", (d) => d.source.x1)
      .attr("x2", (d) => d.target.x0)
      .call((gradient) =>
        gradient
          .append("stop")
          .attr("offset", "0%")
          .attr("stop-color", ({source: {index: i}}) => color(G[i]))
      )
      .call((gradient) =>
        gradient
          .append("stop")
          .attr("offset", "100%")
          .attr("stop-color", ({target: {index: i}}) => color(G[i]))
      );

const linkPathGPath =  linkPathG
    .append("path")
    .attr("d", linkPath)
    .attr(
      "stroke",
      linkColor === "source-target"
        ? ({index: i}) => `url(#${uid}-link-${i})`
        : linkColor === "source"
        ? ({source: {index: i}}) => color(G[i])
        : linkColor === "target"
        ? ({target: {index: i}}) => color(G[i])
        : linkColor
    )
    .attr("stroke-width", ({width}) => Math.max(1, width))
   .call(Lt ? (path) => path.append("title").text(({index: i}) => Lt[i]) : () => {});

linkPathGPath.each(function(d,i) {
    let thisLink = d3.select(this); 
    let thisLinkSource = origLinks[i].source;
    let thisLinkTarget = origLinks[i].target;
    return thisLink.attr("class",`source_${thisLinkSource} target_${thisLinkTarget}`);
    })


    linkPathGPath
        .on("mouseover",function(){
            let thisPath = d3.select(this);
            let thisID = d3.select(this).attr("class");
            thisID = thisID.split(' ');
            let thisSiblings = d3.select(this.parentNode.parentNode).selectAll(`.${thisID[0]}`).filter(`.${thisID[1]}`);
            // return thisPath.attr("stroke-opacity","1");
            return thisSiblings.attr("stroke-opacity","1");
        })
        .on("mouseout",function(){
            let thisPath = d3.select(this);
            let thisID = d3.select(this).attr("class");
            thisID = thisID.split(' ');
            let thisSiblings = d3.select(this.parentNode.parentNode).selectAll(`.${thisID[0]}`).filter(`.${thisID[1]}`);
            // return thisPath.attr("stroke-opacity",linkStrokeOpacity);
            return thisSiblings.attr("stroke-opacity",linkStrokeOpacity);
        })

const svgSelect = d3.select(svg);
console.log(svgSelect.parentNode);

//    linkPathG.call(Lt ? (path) => path.append("rect").attr("width","10").attr("height","10").attr("stroke","black") : () => {});

//   if (Tl)
//     svg
//       .append("g")
//       .attr("font-family", "sans-serif")
//       .attr("font-size", 10)
//       .attr("fill", "currentColor")
//       .selectAll("text")
//       .data(nodes)
//       .join("text")
//       .attr("x", (d) => (d.x0 < width / 2 ? d.x1 + nodeLabelPadding : d.x0 - nodeLabelPadding))
//       .attr("y", (d) => (d.y1 + d.y0) / 2)
//       .attr("dy", "0.35em")
//       .attr("text-anchor", (d) => (d.x0 < width / 2 ? "start" : "end"))
//       .text(({index: i}) => Tl[i])
//       ;

// Add text label to node

  if (Tl)

{
 
 let titleTextList = [];
 node.each((d,i) => {
    let titleText = Tl[i];
    titleText = titleText.split(" ");
    titleTextList.push(titleText);
 })

node.append("text")
      .attr("font-family", "sans-serif")
      .attr("font-size", 10)
      .attr("fill", "black")
      .attr("stroke","none")
      .attr("x", (d) => (d.x0 < width / 2 ? d.x1 + nodeLabelPadding : d.x0 - nodeLabelPadding))
      .attr("y", (d) => (d.y1 + d.y0) / 2)
      //.attr("dy", "0.35em")
      .attr("text-anchor", (d) => (d.x0 < width / 2 ? "start" : "end"))
      .attr("dominant-baseline","middle")
      .each(function(d,i) {
    let thisNode;
    let thisNodeText = titleTextList[i];
    let j = thisNodeText.length;
    thisNodeText = [thisNodeText.slice(0,j-1).join(' '),thisNodeText[(j-1)]];
    thisNodeText = thisNodeText.filter(q => q !== "");
    j = thisNodeText.length;
    for (let k = 0; k < j; k++)
    {let topMarg;
        if (k === 0) {topMarg = `-${(j-1)/2}em`} else {topMarg = "1em"}
        
        thisNode = d3.select(this)
        .append("tspan")
        .attr("dy",topMarg)
        .attr("x", d => (d.x0 < width / 2 ? d.x1 + nodeLabelPadding : d.x0 - nodeLabelPadding))
        .text(thisNodeText[k]);
    }
    return thisNode;
})

}

// add pop-up tooltips to nodes

    if (Tt) {

    const nodeLabelG = node
        .append("g")
        .attr("class","node_label_group")
        .attr("transform", d => {
            const labelTranslate = +`-${(d.y1 - d.y0)/2}`;
            if (d.x0 < width / 2){
            return `translate(${(d.x0) +  5}, ${d.y0}) rotate(-90,0,0) translate(${labelTranslate},${d.x1 - d.x0})`
            }
            return `translate(${(d.x0 - 55)}, ${d.y0})  rotate(-90,0,0) translate(${labelTranslate},0)`
            })
        .attr("opacity","0")
        .attr("overflow","visible")
        .style('pointer-events', 'none')
        ;

    nodeLabelG.append("rect")
        .attr("height","50")
        .attr("width","130")
        .attr("stroke","black")
        .attr("fill","none")
        .attr("filter","drop-shadow(0 3px 4px rgba(0,0,0,.5))")
        ;

    const nodeLabelText = nodeLabelG.append("text")
            .attr("x","5")
            .attr("y",".5em")
            .attr("font-size","11")
            .attr("font-family","sans-serif")
            .attr("font-weight","normal")
            .attr("stroke","none")
            .attr("fill","black")

        nodeLabelText.append("tspan")
            .attr("dy","1em")
            .text((d,i) => {
                let authorID = origNodes[i].author;
                return lookupIDTable.get(authorID);
            })
        nodeLabelText.append("tspan")
            .attr("x","5")
            .attr("dy","1em")
            .attr("font-style","italic")
            .text((d,i) => {
                let workID = origNodes[i].work;
                return lookupIDTable.get(workID);})
        nodeLabelText.append("tspan")
            .attr("x","5")
            .attr("dy","1em")
            .text((d,i) => Tt[i].split("\n")[1])
            ; 


    nodeRect
        .on("mouseover", function(event) {
            //const [x,y] = d3.pointer(event, this);
            d3.select(this).attr("opacity","1");
            d3.select(this.nextSibling.nextSibling)
                .attr("opacity","1")
            d3.select(this.nextSibling.nextSibling.firstChild)
                .attr("fill","white")

                // .attr("transform", `translate(${x},${y}) rotate(-90,0,0)`)
        })
        .on("mouseout", function(event) {
                d3.select(this).attr("opacity",".6");
                d3.select(this.nextSibling.nextSibling)
                .attr("opacity","0")
            d3.select(this.nextSibling.nextSibling.firstChild)
                .attr("fill","none")});

    // nodeLabelG
    //     .on("mouseover", function(event) {
    //        const [x,y] = d3.pointer(event, this);
    //         this
    //             .attr("opacity","1")
    //             .attr("transform", `translate(${x},${y}) rotate(-90,0,0)`)
    //     })
    //     .on("mouseout", function(event) {
    //             this
    //             .attr("opacity","0")});
    }

svg.selectAll(".node")
    .on("mouseover", function(event) {
        d3.select(this).raise();
    })


  function intern(value) {
    return value !== null && typeof value === "object" ? value.valueOf() : value;
  }

  return Object.assign(svg.node(), {scales: {color}, nodes: nodes, links: links});
}

```