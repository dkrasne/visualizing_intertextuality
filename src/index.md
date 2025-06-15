---
title: Visualizing Intertextuality
theme: [wide, air]
toc: false
---

# Visualizing Intertextuality

**Developed by:** [Darcy Krasne](http://www.darcykrasne.com/)

A project to visualize intertexts in Latin poetry using [nodegoat](https://nodegoat.net/), [Observable Framework](https://observablehq.com/framework/), and Python. (See [the about page](./about) for further details.)

View the code on [GitHub](https://github.com/dkrasne/visualizing_intertextuality).

N.B. As Observable is phasing out its cloud hosting, the site will be migrating to http://dkrasne.github.io/visualizing_intertextuality. Please take note of the new address.


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


## Select passage to view

<div class="tip">Currently there is a limited set of intertexts in the database. Choose Valerius Flaccus, <i>Argonautica</i>, Book 1, lines 1&ndash;4 or Book 2, lines 475&ndash;476 to see what the display looks like. You can also <a href="./sankey">view this diagram</a> to get a rough idea of what the full network of intertexts currently looks like.</div>

```js
// Create authors dropdown

const authorList = [];
const authorTable = nodegoatTables.author_table;

/* If there are any surviving bilingual poets, there may need to be a second filtering step at the works table. */

for (let author in authorTable) {
	if (authorTable[author].language === "Latin") {
		const authorSet = [authorTable[author].author_name, authorTable[author].obj_id];
		authorList.push(authorSet);
	}
}

const authorPicker = Inputs.select(new Map([[null,null]].concat(authorList)), {label: "Select author:", value: null, sort: true});
const authorID = view(authorPicker);
```

```js
// Create works dropdown

const workList = [];
const workTable = nodegoatTables.work_table;

for (let work in workTable) {
	if (workTable[work].author_id === authorID) {
		const workSet = [workTable[work].title, workTable[work].obj_id]
		workList.push(workSet);
	}
}

const workPicker = Inputs.select(new Map([[null, null]].concat(workList)), {label: "Select work:", value: null, sort: true});
const workID = view(workPicker);
```

```js
// Create work section dropdown

const workSegList = [];
const workSegTable = nodegoatTables.work_seg_table;

for (let workSeg in workSegTable) {
	let workSegName;
	if (!workSegTable[workSeg].work_section) {	
		workSegName = "all"
	} else if (!workSegTable[workSeg].work_subsection) {
		workSegName = workSegTable[workSeg].work_section;
	} else {
		workSegName = workSegTable[workSeg].work_section + ', ' + workSegTable[workSeg].work_subsection;
	}
	
	if (workSegTable[workSeg].work_id === workID) {
		const workSegSet = [workSegName, workSegTable[workSeg].obj_id];
		workSegList.push(workSegSet);
	}
}

const workSegPicker = Inputs.select(new Map([[null, null]].concat(workSegList)), {label: "Select work section:", value: null, sort: true});
const workSegID = view(workSegPicker);
```

<div class="grid grid-cols-3">
	<div class="card">
		${authorPicker}
	</div>
	<div class="card">
		${workPicker}
	</div>
	<div class="card">
		${workSegPicker}
	</div>
</div>

```js
const passageDetails = {};

for (let author in authorTable) {
	if (authorTable[author].obj_id === authorID) {
		passageDetails.authorName = authorTable[author].author_name;
	}
}

for (let work in workTable) {
	if (workTable[work].obj_id === workID) {
		passageDetails.workTitle = workTable[work].title;
	}
}

for (let workSeg in workSegTable) {
	
	if (workSegTable[workSeg].obj_id === workSegID) {	
		let workSegName;
		if (!workSegTable[workSeg].work_subsection) {
			workSegName = workSegTable[workSeg].work_section;
		} else {
			workSegName = workSegTable[workSeg].work_section + ', ' + workSegTable[workSeg].work_subsection;
		}
		
		passageDetails.workSegName = workSegName;
	}
}
```

```js
// Create necessary variables for chart display

const workSegVars = {
	workSegLineMin: 1,
	workSegLineMax: null,
	workSegMeterID: null
};

// Set variables for chart display, based on work segment chosen

for (let workSeg in workSegTable) {
	if (workSegTable[workSeg].obj_id === workSegID) {
		workSegVars.workSegLineMin = workSegTable[workSeg].first_line;
		workSegVars.workSegLineMax = workSegTable[workSeg].last_line;
		workSegVars.workSegMeterID = workSegTable[workSeg].meter_id;
		break;
	}
}

```

```js
// Create number pickers for range of lines to display

const lineMinPicker = Inputs.number([workSegVars.workSegLineMin, workSegVars.workSegLineMax], 
									{step: 1, 
									label: "Select starting line: ", 
									value: workSegVars.workSegLineMin, 
									placeholder: workSegVars.workSegLineMin});
const startLine = view(lineMinPicker);
```

```js
let tempMax = Math.min(workSegVars.workSegLineMin + 19, Math.max(workSegVars.workSegLineMin,workSegVars.workSegLineMax))

const lineMaxPicker = Inputs.number([workSegVars.workSegLineMin, workSegVars.workSegLineMax], 
									{step: 1, 
									label: "Select ending line: ", 
//									value: workSegVars.workSegLineMin + 19, 
									value: tempMax, 
									placeholder: workSegVars.workSegLineMax});
const endLine = view(lineMaxPicker);
```

<div class="grid grid-cols-2">
<div class="card">
${lineMinPicker}
</div>
<div class="card">
${lineMaxPicker}
</div>
</div>

```js
// Set default numbers

const lineRange = {
	firstLine: 1,
	lastLine: function() {return this.firstLine + 20;},
}


if (startLine > 0) {
	lineRange.firstLine = startLine;
}

if (endLine >= startLine) {
	lineRange.lastLine = endLine;
} else {lineRange.lastLine = lineRange.firstLine + 0;}
```

```js
// Establish metrical positions

const meterID = workSegVars.workSegMeterID;
let positions;
let meterLen;
let linePattern;

for (let meter in meters) {
	if (meters[meter].meter_id === meterID) {
		positions = meters[meter].positions;
		meterLen = meters[meter].max_line_beats;
		linePattern = meters[meter].recur_line_pattern;
	}
}

const meterPosArr = d3.range(1, meterLen+1);
let linePatternArr = d3.range(1,linePattern+1);

let i = 1;
if (linePattern === 1) {		// for stichic meters
	for (let pos in positions) {
		const posBeats = positions[pos].pos_len;
		positions[pos].gridNums = [];
		for (let j = 0; j < posBeats; j++) {
			positions[pos].gridNums.push(i);
			i += 1;
		}
	}
} else {	// for meters with stanzas or multi-line patterns
	for (let line in linePatternArr){
		let currPatternLine = linePatternArr[line];
		i = 1;
		for (let pos in positions) {
			if (positions[pos].unit_line === currPatternLine) {
				const posBeats = positions[pos].pos_len;
				positions[pos].gridNums = [];
				for (let j = 0; j < posBeats; j++) {
					positions[pos].gridNums.push(i);
					i += 1;
				}
			}
		}
	}
}

```

<!-- Prepare intertexts for display -->

```js
// Build word-level intertexts

const wordInstTable = nodegoatTables.word_instance_table;
const wordInstArr = [];

for (let inst in wordInstTable) {
	if (wordInstTable[inst].work_segment_id === workSegID) {
		wordInstArr.push(wordInstTable[inst])
	}
}

const wordsFiltered = wordInstArr.filter(inst => inst.line_num >= lineRange.firstLine && inst.line_num <= lineRange.lastLine);
const lineArr = d3.range(lineRange.firstLine, lineRange.lastLine+1);
```


```js
// Get intertexts

const wordLvlIntxts = nodegoatTables.word_lvl_intxt_table;

if (wordsFiltered.length === 0) {wordsFiltered.push(
	{obj_id: "",
  word: "",
  lemma_id: "",
  work_segment_id: "",
  line_num: 0,
  line_num_modifier: null,
  start_pos_id: "",
  end_pos_id: ""}
)}

for (let word in wordsFiltered) {
	wordsFiltered[word].posIDs = [];
	wordsFiltered[word].directIntertexts = 0;
	wordsFiltered[word].indirectIntertexts = 0;
	wordsFiltered[word].directIntertextIDs = [];
	wordsFiltered[word].indirectIntertextIDs = [];

// Assign all spanned positions to word

	let posMatch = false;
	for (let posn in positions) {
		if (wordsFiltered[word].start_pos_id === positions[posn].meter_pos_len_id) {
			posMatch = true;
		}
		if (posMatch === true) {
			wordsFiltered[word].posIDs.push(positions[posn].meter_pos_len_id);		
		}
		if (wordsFiltered[word].end_pos_id === positions[posn].meter_pos_len_id) {
			posMatch = false;
			break;
		}
	}

// Gather direct intertexts
	
	for (let intxt in wordLvlIntxts) {
		if (wordLvlIntxts[intxt].target_word_id === wordsFiltered[word].obj_id) {	// check each intertext to see if the current word is its target
			let sourceID = wordLvlIntxts[intxt].source_word_id;		// if so, set 'sourceID' to the respective source word
			wordsFiltered[word].directIntertexts += 1;		// increment the number of direct intertexts
			wordsFiltered[word].directIntertextIDs.push(sourceID);	// add the source word to the list of direct intertexts
		}
	}

// Gather indirect intertexts based on direct intertexts

	const checkedIDs = [];
	for (let i in wordsFiltered[word].directIntertextIDs) {
		let id = wordsFiltered[word].directIntertextIDs[i];
		for (let intxt in wordLvlIntxts) {
			if (wordLvlIntxts[intxt].target_word_id === id) {		// check each intertext to see if a direct intertext source is also the target of another intertext
				let sourceID = wordLvlIntxts[intxt].source_word_id;		// if so, set 'sourceID' to the respective source word
				if (!wordsFiltered[word].indirectIntertextIDs.includes(sourceID) && !wordsFiltered[word].directIntertextIDs.includes(sourceID)) {
					wordsFiltered[word].indirectIntertextIDs.push(sourceID);	// if the relevant source word isn't already included in the direct or indirect intertexts, add it to the list of indirect intertexts
				} 
			}
		}
		checkedIDs.push(id);
	}

// Gather indirect intertexts based on indirect intertexts
	
	let j = checkedIDs.length;
	do {
	for (let i in wordsFiltered[word].indirectIntertextIDs) {
		let id = wordsFiltered[word].indirectIntertextIDs[i];
		if (!checkedIDs.includes(id)){
		for (let intxt in wordLvlIntxts) {
			if (wordLvlIntxts[intxt].target_word_id === id) {
				let sourceID = wordLvlIntxts[intxt].source_word_id;	
				if (!wordsFiltered[word].indirectIntertextIDs.includes(sourceID) && !wordsFiltered[word].directIntertextIDs.includes(sourceID)) {
					wordsFiltered[word].indirectIntertextIDs.push(sourceID);
					}
				}
			}
		}
		checkedIDs.push(id);
		j += 1;
	}} while (j < checkedIDs.length);

	wordsFiltered[word].indirectIntertexts = wordsFiltered[word].indirectIntertextIDs.length;
}
	
const intertextsArrComplete = [];

for (let line in lineArr) {
	for (let i in meterPosArr) {
		let intertextObj = {};
		intertextObj.lineNum = lineArr[line];
		intertextObj.linePos = meterPosArr[i];
		intertextObj.intxtCnt = 0;
		for (let posn in positions) {
			if (positions[posn].gridNums.includes(meterPosArr[i])) {
				intertextObj.linePosID = positions[posn].meter_pos_len_id;
				break;
			}
		}
		for (let word in wordsFiltered) {
			if (wordsFiltered[word].line_num === intertextObj.lineNum && wordsFiltered[word].posIDs.includes(intertextObj.linePosID)) {
				intertextObj.wordObj = wordsFiltered[word];
				intertextObj.intxtCnt = wordsFiltered[word].directIntertexts + wordsFiltered[word].indirectIntertexts;
				intertextObj.word = wordsFiltered[word].word;
			}
		}
		
		intertextsArrComplete.push(intertextObj);
	}
}

const intertextsArr = intertextsArrComplete.filter(pos => pos.word); // only include cells that have a word assigned to them

// Get final intertext counts, in order to set tick range

const intxtCnts = [];

if (intertextsArr.length > 0) {
	for (let i in intertextsArr) {
		intxtCnts.push(intertextsArr[i].intxtCnt);
	}
}

```


## Visualization

<!-- Create grid -->

```js
// Define grid width based on the selection's meter.

let gridX;

for (let meter in meters) {
	if (meters[meter].meter_id === meterID) {
		gridX = meters[meter].max_line_beats
	}
}

// Define grid height based on number of lines.

const gridY = (lineRange.lastLine - lineRange.firstLine) + 1;  // I may need to modify this to accomodate passages with extra lines

const cellSize = 20;
const gridHeight = gridY * cellSize;
const gridWidth = gridX * cellSize;
```

<!--
The grid will be ${gridX} cells wide.
The grid will be ${gridY} cells tall.
-->


```js
// Create plot, conditional on the existence of intertexts

const plotDisplay = intertextsArr.every(intxt => intxt.intxtCnt === 0) ? null : Plot.plot({
	grid: true,
	x: {
		label: null, 
		domain: d3.range(1,gridX+1),
		padding: 0,
		axis: null,
		},
	y: {
		label: 'Line', 
		domain: d3.range(lineRange.firstLine, lineRange.lastLine +1),
		tickSize: 0,
		},
	color: {scheme: "Greens", 
		legend: true, 
		label: "Total Intertexts (direct & indirect)",
		ticks: d3.range(Math.min(...intxtCnts), Math.max(...intxtCnts)+1),
		tickFormat: d => Math.floor(d),
		},
	marks: [
		Plot.cell(intertextsArr, {
			x: "linePos",
			y: "lineNum",
			fill: d => d.wordObj.directIntertexts + d.wordObj.indirectIntertexts,
			tip: {format: {
				word: true,
				x: false,
				y: false,
				lineNum: true,
				fill: false
			}},
			channels: {
				title: d => `${d.wordObj.word} (line ${d.lineNum})\n# direct intertexts: ${d.wordObj.directIntertexts}\n# indirect intertexts: ${d.wordObj.indirectIntertexts}`,
				word: d => d.wordObj.word,
				lineNum: {
					value: "lineNum",
					label: "line"
				},
				dirIntxt: {
					value: d => d.wordObj.directIntertexts,
					label: "# direct intertexts"
				},
				indIntxt: {
					value: d => d.wordObj.indirectIntertexts,
					label: "# inherited intertexts"
				},
			},
		})
	],
	style: {fontSize: "12pt"},
	width: gridWidth + 120,
	height: gridHeight + 50,
	marginTop: 20,
	marginRight: 50,
	marginBottom: 30,
	marginLeft: 70
});

```

```js
const plotCurrSelect = !plotDisplay ? null : Generators.input(plotDisplay);
```

```js
let bgColor = "#ccccff"; // this is a nice blue that works well
/* the following are attempts to make a more "papyrus"-like background that still contrasts with the lightest green */
/*
bgColor = "#ddcc88";
bgColor = "#daba91"; // taken from an actual papyrus pixel
bgColor = "#ccaf87"; // taken from an actual papyrus pixel
bgColor = "#d4b48c"; // average of the previous two colors
*/

if (!plotDisplay) {
	display(html`<p>Based on information currently in the database, there are no intertexts in the specified passage.</p>`)
} else {

display(

html`<p style="max-width:none; font-size:smaller;">Click on a cell to freeze the popup information. <b>Direct intertexts</b> are those where a scholar has suggested a direct link between the present word and a word in an earlier text. <b>Indirect intertexts</b> are intertexts at further remove (i.e., where a direct or indirect intertext refers to another, still earlier, passage). Currently, the project does not include intratexts (allusions to other passages within the same text).</p>

<p style="max-width:none; font-size:smaller;"><b>Two caveats:</b> absence of a word does not necessarily mean that there are no intertexts, just that they are not yet in the database; and lines appear in numeric order, even if editors agree that they should be transposed.</p></div>

<div class="grid grid-cols-2"><div class="card" style="background-color:${bgColor}; padding-top: 30px;">

<h2 style="padding-bottom: 10px;">${passageDetails.authorName}, <i>${passageDetails.workTitle}</i>, ${passageDetails.workSegName}: lines ${lineRange.firstLine}&ndash;${lineRange.lastLine}</h2>

${plotDisplay}
</div>
<div>
	<p>Eventually there will be a network visualization in this space. For now, you can see <a href="./sankey">a diagram of the full set of available intertexts</a> to get a sense of what that visualization might look like.</p>
	<p><i>The following information will eventually not be displayed.</i></p>
	<p>Selected word object ID: ${plotCurrSelect ? plotCurrSelect.wordObj.obj_id : "none"}<br>
	Selected word: ${plotCurrSelect ? plotCurrSelect.word : "none"}</p>
</div>
</div>`
)}

```

```js
if (!plotDisplay) {display(html`<p></p>`)}
else {
	display(html`<p>The selected datapoint, which will serve as the starting point of the generated network (this will eventually not be displayed):</p>`)
	if (plotCurrSelect) {display(plotCurrSelect)} else {display(html`<p><i>No current selection in plot.</i></p>`)}
	}
```

<hr>

<!--

## Attempting network

```js
const width = 640;
const height = 640;

const links = graphData.links.map((d) => Object.create(d));
const nodes = graphData.nodes.map((d) => Object.create(d));

const color = d3.scaleOrdinal(d3.schemeObservable10);

const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id((d) => d.id))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2))
    .on("tick", ticked);

const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .attr("style", "max-width: 100%; height: auto;");


// a combination of ChatGPT and Elijah Meeks
const marker = svg.append("defs")
	.append("marker")
  .attr("id", "arrow")
  .attr("viewBox", "0 0 10 10")
  .attr("refX", 20)
  .attr("refY", 5)
  .attr("markerUnits", 'userSpaceOnUse')
  .attr("markerWidth", 6)
  .attr("markerHeight", 6)
  .attr("orient", "auto")
  .append("path")
  .attr("d", "M 0 0 L 10 5 L 0 10 z")
  .attr("fill", "black")
  .attr("fill-opacity", 0.6);

const link = svg.append("g")
    .attr("stroke", "var(--theme-foreground-faint)")
    .attr("stroke-opacity", 0.6)
  .selectAll("line")
  .data(links)
  .join("line")
    .attr("stroke-width", (d) => Math.sqrt(d.weight))
	.attr("marker-end", "url(#arrow)");

const node = svg.append("g")
    .attr("stroke", "var(--theme-background)")
    .attr("stroke-width", 1.5)
  .selectAll("circle")
  .data(nodes)
  .join("circle")
    .attr("r", (d) => {
    let proto = Object.getPrototypeOf(d);
	let numProps = Object.keys(proto).length - 2;
    return Math.sqrt(numProps) * 5})
    .attr("fill", (d) => color(d.author))
    .call(drag(simulation));

node.append("title")
    .text((d) => lookupIDTable.get(d.id).section ? `${lookupIDTable.get(d.id).work}, ${lookupIDTable.get(d.id).section}` : lookupIDTable.get(d.id).work);

function ticked() {
  link
      .attr("x1", (d) => d.source.x)
      .attr("y1", (d) => d.source.y)
      .attr("x2", (d) => d.target.x)
      .attr("y2", (d) => d.target.y);

  node
      .attr("cx", (d) => d.x)
      .attr("cy", (d) => d.y);
}

display(svg.node());
```

```js
function drag(simulation) {

  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }

  function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }

  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }

  return d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
}
```
```js
nodes
```
```js
links
```


```js
// Create maps to store total counts and assign indices for each source-target pair.
const edgeCountMap = new Map();
const edgeIndexMap = new Map();

// Loop through links to annotate them.
graphData.links.forEach(link => {
  // Assume link.source and link.target are objects with an "id" property.
  const key = `${link.source.id}-${link.target.id}`;
  // Get the current index for this pair (starting at 0).
  const currentIndex = edgeIndexMap.get(key) || 0;
  // Assign this edge its index.
  link.edgeIndex = currentIndex;
  // Update the index for the next edge.
  edgeIndexMap.set(key, currentIndex + 1);
  // Also count the total number of edges for this pair.
  edgeCountMap.set(key, (edgeCountMap.get(key) || 0) + 1);
});

// (Optional) Log the edge counts to verify.
// console.log("Edge counts:", [...edgeCountMap.entries()]);

```

```js

const links2 = graphData.links.map((d) => Object.create(d));
const nodes2 = graphData.nodes.map((d) => Object.create(d));


const svg2 = html`<svg width=800 height=600 style="border:1px solid black"><defs></defs></svg>`;

const simulation2 = d3.forceSimulation(nodes2)
    .force("link", d3.forceLink(links2).id((d) => d.id))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2))

const selection = d3.select(svg2);

// Define a small offset to prevent overlap (adjust as needed)
const linkOffset = 3;
const curveStrength = 30; // Adjust curve height

// Find min/max values in your node positions
const xExtent = d3.extent(nodes2, d => d.x);
const yExtent = d3.extent(nodes2, d => d.y);

// Create scaling functions to map node positions to canvas size
const xScale = d3.scaleLinear().domain(xExtent).range([50, 750]); // Keep some margin
const yScale = d3.scaleLinear().domain(yExtent).range([50, 550]);

d3.select(svg2)
  .selectAll("path")
  .data(links2)
  .join("path")
  .attr("d", d => {
    const x1 = xScale(d.source.x);
    const y1 = yScale(d.source.y);
    const x2 = xScale(d.target.x);
    const y2 = yScale(d.target.y);
    
    const key = `${d.source.id}-${d.target.id}`;
    const totalEdges = edgeCountMap.get(key); // Total edges for this pair
    const index = d.edgeIndex;               // This edge's index
    
    // Calculate curve offset.
    // The formula centers the edges: if there is an odd number, the middle edge is straight;
    // if even, they are symmetrically curved.
    const curveOffset = ((index + 1) - (totalEdges + 1) / 2) * curveStrength;
    
    // Compute midpoint for the quadratic Bézier curve.
    const midX = (x1 + x2) / 2;
    const midY = (y1 + y2) / 2 - curveOffset;
    
    return `M ${x1},${y1} Q ${midX},${midY} ${x2},${y2}`;
  })
  .attr("fill", "none")
  .attr("stroke", "black")
  .attr("stroke-width", 1);

/* 
// Apply scaling when setting positions
// Draw offset links (edges)
selection
  .selectAll("line")
  .data(graphData.links)
  .join("line")
  .attr("x1", d => xScale(d.source.x) + (d.key ? linkOffset * (d.key % 2 ? 1 : -1) : 0))
  .attr("y1", d => yScale(d.source.y) + (d.key ? linkOffset * (d.key % 2 ? -1 : 1) : 0))
  .attr("x2", d => xScale(d.target.x) + (d.key ? linkOffset * (d.key % 2 ? -1 : 1) : 0))
  .attr("y2", d => yScale(d.target.y) + (d.key ? linkOffset * (d.key % 2 ? 1 : -1) : 0))
  .attr("stroke", "black")
  .attr("stroke-width", 1);
*/

// Draw nodes (circles)
selection
  .selectAll("circle")
  .data(nodes2)
  .join("circle")
  .attr("cx", d => xScale(d.x))
  .attr("cy", d => yScale(d.y))
  .attr("r", 5)
  .attr("fill", "black");




const defs = d3.select(svg2).select("defs");

defs.append("marker")
  .attr("id", "arrow")
  .attr("viewBox", "0 0 10 10")
  .attr("refX", 20)
  .attr("refY", 5)
  .attr("markerWidth", 6)
  .attr("markerHeight", 6)
  .attr("orient", "auto")
  .append("path")
  .attr("d", "M 0 0 L 10 5 L 0 10 z")
  .attr("fill", "black");

// Now, update the edges to use the arrowheads
d3.select(svg2)
  .selectAll("path")
  .attr("marker-end", "url(#arrow)");


```

```js
view(svg2)
```

-->

<hr>

## Data

<details>
<summary>Click here to view the full data.</summary>

Raw data from nodegoat (extracted into separate objects):

```js
nodegoatModel
```

Data after initial transformation:

```js
nodegoatTables
```
```js
meters
```
```js
intertextsTable
```

</details>

<hr>

# Sandbox

Everything below here will not be in the final project.

## Data Checks

`nodegoatModel`:

```js
nodegoatModel
```

`nodegoatTables`:

```js
nodegoatTables
```

`positions` (metrical positions):

```js
positions
```

`wordsFiltered`:

```js
wordsFiltered
```

`intertextsArr`:

```js
intertextsArr
```

Meters:

```js
meters
```

`graphData`:
```js
graphData
```

`sankeyData`:
```js
sankeyData
```

`lookupIDTable`:
```js
lookupIDTable
```


<hr>

## Testing stuff goes below here.

```js
csvSamp
```

```js
const workArr = [];
for (let item in csvSamp) {
	if (item !== 'columns') {
		let work = csvSamp[item].work
		if (!workArr.includes(work)) {
			workArr.push(work);
		}
	}
};
const work = view(Inputs.select([null].concat(workArr), {label: "Work"}))
```

The selected work is *${work}*.

<!-- Some information on Framework's reactivity: https://medium.com/@stxmendez/how-observable-implements-reactive-programming-784bcc02382d -->

```js
const csvItems = [];
for (let item in csvSamp) {
	csvItems.push(item);
}
```

```js
csvItems
```


```
let lineMin;
let lineMax;

lineMin = 1; // this will actually need to change depending on the range of the selection
lineMax = 10; // this will actually need to change depending on the range of the selection

const lineRange = [];

for (let i = lineMin; i <= lineMax; i++) {
	lineRange.push(i);
}
```

```
lineRange
```

```
const numX = workArr.length; // this will actually be determined by the appropriate length for a given meter
const numY = lineRange.length;
const cellSize = 20;
const gridHeight = numY * cellSize;
const gridWidth = numX * cellSize;
```

```
Plot.plot({
	color: {scheme: "Blues", legend: true},
	marks: [
		Plot.cell(
			csvSamp,
			Plot.group(
				{fill: "count"},
				{
					x: "work",
					y: "line",
					fill: "word",
//					filter: (d) => d.line >= lineMin && d.line <= lineMax && d.work === work,
					filter: null,
					tip: true // Info on customizing tooltip using 'format': https://observablehq.com/plot/marks/tip
				}
			)
		),
//		Plot.axisY({ticks: []}),
	],
	x: {
		padding: 0, 
		axis: "both",  // set to null for no axis
		tickRotate: -30,
//		label: null  // use this to remove the label for the axis
	},
	y: {
		padding: 0, 
		domain: d3.range(lineMin, lineMax + 1),
		tickSize: 0
	},
	width: gridWidth + 100,
	height: gridHeight + 100,
	marginTop: 50,
	marginRight: 50,
	marginBottom: 50,
	marginLeft: 50
})
```




```js
const csvSamp = FileAttachment("data/sample_csv_loader.csv").csv({typed: true})
```

```js
Inputs.table(csvSamp)
```
