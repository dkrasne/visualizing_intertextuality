---
title: Visualizing Intertextuality
theme: [wide, air]
toc: false
---

# Visualizing Intertextuality

**Developed by:** [Darcy Krasne](http://www.darcykrasne.com/)

A project to visualize intertexts in Latin poetry using [nodegoat](https://nodegoat.net/), [Observable Framework](https://observablehq.com/framework/), [Python](https://www.python.org/), and [D3.js](https://d3js.org/). ([See the about page](./about) for further details, or [view the code on GitHub](https://github.com/dkrasne/visualizing_intertextuality).)

*N.B. As Observable is phasing out its cloud hosting, this site will be migrating to http://dkrasne.github.io/visualizing_intertextuality. Please take note of the new address.*

## Select passage to view

<div class="tip">Currently there is a limited set of intertexts in the database. Choose Valerius Flaccus, <i>Argonautica</i>, Book 1, lines 1&ndash;4 or Book 2, lines 475&ndash;476 to see what the display looks like. You can also <a href="./sankey">view this diagram</a> to get a rough idea of what the full network of intertexts currently looks like.</div>

<!-- Author, Work, and Work Section Selectors -->

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

<!-- Starting and Ending Line Selectors -->

<div class="grid grid-cols-2">
<div class="card">
${lineMinPicker}
</div>
<div class="card">
${lineMaxPicker}
</div>
</div>

## Visualizations


<!-- Webpage -->

```js
let bgColor = "#ccccff";

if (!plotDisplay) {
	display(html`<p style="max-width:none">Based on information currently in the database, there are no intertexts in the specified passage (or you have made no selection yet).</p>`)
} else {

display(

html`
<div class="grid grid-cols-2">
	<div class="card" style="background-color:${bgColor}; padding-top: 30px;">

		<h2 style="padding-bottom: 10px;">${passageDetails.authorName}, <i>${passageDetails.workTitle}</i>, ${passageDetails.workSegName}: lines ${lineRange.firstLine}&ndash;${lineRange.lastLine}</h2>

		${plotDisplay}

		${removedMonosyllables.length > 0 ? display(
			html`
			<p style="max-width:none; font-size:smaller;">N.B. ${removedMonosyllables.length} elided ${removedMonosyllables.length === 1 ? 'monosyllable' : 'monosyllables'} ${removedMonosyllables.length === 1 ? 'is' : 'are'} not shown above: elided monosyllables are only shown when the word following them either is itself not in the database or has no intertexts in the database.</p>
			`
		) : null}

	</div>

	<div>
		<h4>How to use this chart</h4>
		<p style="font-size:smaller;">Click on a cell to freeze the popup information. <b>Direct intertexts</b> are those where a scholar has suggested a direct link between the present word and a word in an earlier text. <b>Indirect intertexts</b> are intertexts at further remove (i.e., where a direct or indirect intertext refers to another, still earlier, passage). Currently, the project does not include intratexts (allusions to other passages within the same text).</p>

		<p style="font-size:smaller;"><b>Two caveats:</b> absence of a word does not necessarily mean that there are no intertexts, just that they are not yet in the database; and lines appear in numeric order, even if editors agree that they should be transposed.</p>

		<p style="font-size:smaller;">A <b>missing</b> word (represented as a gap) is not currently in the database. A word shown with <b>zero total intertexts</b> is either in the database only as the ancestor of another word, or has not yet been assigned to any intertextual relationships.</p>

		<p style="font-size:smaller;">For a fuller explanation of the data and its representation, see <a href="./about">the About page</a>.</p>
	</div>
</div>

<div class="grid grid-cols-2" style="margin-top: 2em;">
	<div>
		${
			display(html`
			<h4>The intertextual ancestry of the selected passage</h4>
			<p style="font-size:smaller;">A full explanation of how to read and interact with the chart below (and its current limitations) can be found on <a href="./sankey">the Full Intertext Diagram page</a>.</p>
			${display(sectionSankey)}`)
		}
	</div>
	<div>
		${!plotCurrSelect ? display(html`<p style="border: 2px solid black; padding: 1em;"><i>Mouse over a &ldquo;word&rdquo; block in the passage display in order to see the lineage for that particular word. (Click on the word to freeze the display.)</i></p>`) :
		display(html`
			<h4 style="max-width:none;">The intertextual lineage of <i>${plotCurrSelect.word}</i> (line ${plotCurrSelect.wordObj.line_num})</h4>
			<p style="font-size:smaller;">This visualization shows both the intertextual ancestry and descent of the selected word. Mouse over a rectangular node to see what text a given word occurs in; mouse over a link between two words to see what type(s) of allusive referentiality connect those two words.</p>
				${wordSankey ? display(wordSankey) : display(html`<p><b><i>The selected word has no intertexts in the database.</i></b></p>`)}
		`)
		}
	</div>
</div>
`
)}

```

<hr>

```js
if (!plotDisplay) {display(html`<p></p>`)}
else {
	display(html`<p>The selected datapoint, which will serve as the starting point of the generated network (this will eventually not be displayed):</p>`)
	if (plotCurrSelect) {display(plotCurrSelect)} else {display(html`<p><i>No current selection in plot.</i></p>`)}
	}
```

<hr>


<!-- DATA LOADING AND MANIPULATION; VISUALIZATION CREATION -->


<!-- Load data -->

```js
import {createLookupIDTable, authorColors} from './js/global_constants.js';
import {SankeyChart} from './js/sankey_function.js';
```

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
// Attach full list of intertexts (used for network and Sankey charts)
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
const lookupIDTable = createLookupIDTable(nodegoatTables);
```
<!-- End mapping -->


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

const lineArr = d3.range(lineRange.firstLine, lineRange.lastLine+1);

const removedMonosyllables = [];

// If an elided monosyllable and the following word are both present in the list of words with intertexts, remove the elided monosyllable; if the following word is present but has no intertexts, remove it from the list instead.
for (let i in wordsFiltered) {
	let word = wordsFiltered[i];
	// check whether each word is an elided monosyllable
	if (word.elided_monosyllable === true) {
		// check whether the following word is in the database
		let overlapCheck = wordsFiltered.filter(checkWord => checkWord.line_num === word.line_num && checkWord.start_pos_id === word.start_pos_id);
		if (overlapCheck.length > 1) {
			let checkWord = overlapCheck.filter(remainingWord => remainingWord.obj_id !== word.obj_id)[0];
			// if the following word has any intertexts, don't show the elided monosyllable
			if (checkWord.directIntertexts + checkWord.indirectIntertexts > 0) {
				let removedWord = wordsFiltered.splice(i, 1);
				removedMonosyllables.push(removedWord);
			}
			// if the following word has no intertexts, don't show it, and keep the elided monosyllable
			else {
				let followingWordIndex = wordsFiltered.findIndex(item => item.obj_id === checkWord.obj_id);
				let removedWord = wordsFiltered.splice(followingWordIndex, 1);
			}
		}
	}
}


// Get intertexts

const wordLvlIntxts = nodegoatTables.word_lvl_intxt_table;

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

<!-- VISUALIZATIONS -->

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
// Assign whichever cell is selected in the cell chart to a constant
const plotCurrSelect = !plotDisplay ? null : Generators.input(plotDisplay);
```

<!-- Intertext Sankeys (passage-level and word-level) -->

<!-- Data preparation -->

```js
// data prep for chart if no word is selected: filtered work-section Sankey diagram (=full intertext diagram) based on current passage


// Get the IDs of all words involved in intertexts in the currently-selected passage
let passageWordIntxts = wordsFiltered.length > 0 ? 
		Array.from(new Set(wordsFiltered.map(word => word.directIntertextIDs.concat(word.indirectIntertextIDs)).flat())) : 
		[];

// Filter the full table of intertexts to just those that include the relevant words
const intertextsTableCopy = JSON.parse(JSON.stringify(intertextsTable));
let passageIntxts = intertextsTableCopy.filter(intxt => passageWordIntxts.includes(intxt.source_word_id) || passageWordIntxts.includes(intxt.target_word_id));

// Get the IDs for those intertexts, both the word-level intertext IDs and the word-level intertext group IDs
let intxtIDs = passageIntxts.map(intxt => [intxt.intxt_grp_id, intxt.intxt_id]).flat().filter(id => id !== null);

// FILTER SANKEY DATA //

// Filter the work-segment edges based on those intertexts
let sankeyEdges = JSON.parse(JSON.stringify(sankeyData.edges)); // prevents the filtering from affecting the actual data
let sankeyFilteredEdgesArr =  sankeyEdges.filter(edge => intxtIDs.includes(edge.id));

// Remove words from those edges that aren't included in the current selection (target words should only be words in the selected passage, and source words should only be those that the current passage has intertexts with)
for (let i in sankeyFilteredEdgesArr) {
	let edge = sankeyFilteredEdgesArr[i];
	edge.source_words = edge.source_words.filter(wordID => passageWordIntxts.includes(wordID));
	let wordList = wordsFiltered.map(word => word.obj_id);
	edge.target_words = edge.target_words.filter(wordID => wordList.includes(wordID) || passageWordIntxts.includes(wordID));
}

// Remove any edges that now have empty target-word lists
const sankeyFilteredEdges = sankeyFilteredEdgesArr.filter(edge => edge.target_words.length > 0);

// Recalculate the weight of those edges
sankeyFilteredEdges.forEach(edge => edge.num_words = (edge.source_words.length + edge.target_words.length)/2);

// Filter the nodes to just those work segements that still have edges connected

const sankeyFilteredNodes = sankeyData.nodes.filter(node => sankeyFilteredEdges.map(edge => edge.source).concat(sankeyFilteredEdges.map(edge => edge.target)).includes(node.name));

```

```js
// data prep for chart if a word is selected: Sankey based on word-to-word connections

const ancestorIntertexts = [];
const descendantIntertexts = [];

let currWordId;
let ancestorWordIDs = [];
let descendantWordIDs = [];

if (plotCurrSelect) {
	
	currWordId = plotCurrSelect.wordObj.obj_id;	// set current word ID to the selected word

	// create functions for getting a word's immediate ancestors or descendants
	function getWordAncestors(currWordId){
		for (let i in intertextsTable) {
			let intxt = intertextsTable[i];
			// for each intertext in the intertexts table, if its target ID matches the focus word (either the selected word or one of its ancestors), add it to the list of ancestor intertexts and add its source to the list of words to be processed.
			if (currWordId === intxt.target_word_id) {
				ancestorIntertexts.push(intxt);
				ancestorWordIDs.push(intxt.source_word_id);
			}
		}
	}
	function getWordDescendants(currWordId){
		for (let i in intertextsTable) {
			let intxt = intertextsTable[i];
			// for each intertext in the intertexts table, if its source ID matches the focus word (either the selected word or one of its descendants), add it to the list of descendant intertexts and add its target to the list of words to be processed.
			if (currWordId === intxt.source_word_id) {
				descendantIntertexts.push(intxt);
				descendantWordIDs.push(intxt.target_word_id);
			}
		}
	}

	getWordAncestors(currWordId);
	getWordDescendants(currWordId);

	while (ancestorWordIDs.length > 0) {
		currWordId = ancestorWordIDs[0];
		getWordAncestors(currWordId);
		ancestorWordIDs.shift();
	}

	while (descendantWordIDs.length > 0) {
		currWordId = descendantWordIDs[0];
		getWordDescendants(currWordId);
		descendantWordIDs.shift();
	}
}

const intertextsWordFiltered = Array.from(new Set(ancestorIntertexts.concat(descendantIntertexts)));

const wordIntxtNodeIDs = Array.from(new Set(intertextsWordFiltered.map(intxt => (Object.values({source_word_id: intxt.source_word_id, target_word_id: intxt.target_word_id}))).flat()));

let wordInstanceTable = JSON.parse(JSON.stringify(nodegoatTables.word_instance_table));
const wordIntxtNodes = wordIntxtNodeIDs.map(id => wordInstanceTable.filter(word => word.obj_id === id)[0]);
wordIntxtNodes.forEach(obj => obj.id = obj.obj_id);
wordIntxtNodes.forEach(obj => delete obj.obj_id);
for (let i in wordIntxtNodes) {
	if (wordIntxtNodes[i].id === plotCurrSelect.wordObj.obj_id) {
		wordIntxtNodes[i].color = "#0088ff";
	}
}

const wordIntxtEdges = [];

for (let i in intertextsWordFiltered) {
	let intxt = intertextsWordFiltered[i];
	wordIntxtEdges.push({source: intxt.source_word_id, target: intxt.target_word_id, value: 1, id: intxt.intxt_id, matchTypes: intxt.match_type_ids});
}
```

<!-- Sankey charts -->

```js
const nodes = [];
  
for (let node in sankeyFilteredNodes) {
  nodes.push({
    id: sankeyFilteredNodes[node].name,
    author: sankeyFilteredNodes[node].author,
    work: sankeyFilteredNodes[node].work
  });
}
```

```js
const links = [];

 for (let i in sankeyFilteredEdges) {
   let edge = sankeyFilteredEdges[i];
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
// Create work section Sankey chart for selected passage

const sectionSankey = nodes.length > 0 && links.length > 0 ? 
	SankeyChart({nodes: nodes, links: links, lookupIDTable: lookupIDTable},
		{
			nodeGroup: d => d.author,
			nodeLabel: d => {
							let nodesFilter = nodes.filter(node => node.id === d.id);
							let nodeAuthorID;
							for (let n in nodesFilter) {nodeAuthorID = nodesFilter[n].author}
							return lookupIDTable.get(nodeAuthorID);
							},
			nodeTitle: d => `${lookupIDTable.get(d.id).work}\n${lookupIDTable.get(d.id).section}`,
			nodeSort: (a,b) => {
				let nodeA = sankeyData.nodes.find(work => work.name === a.id);
				let nodeB = sankeyData.nodes.find(work => work.name === b.id);
				// Sort so that authors go A-Z left-to-right (= bottom-to-top); d3.descending returns -1, 0, or 1
				let authorComp = d3.descending(lookupIDTable.get(nodeA.author), lookupIDTable.get(nodeB.author));
				if (authorComp !== 0) return authorComp; // if the authors aren't the same, don't go any further in sorting
				// Within authors, sort so that all work sections are in order by work
				// eventually may sort additionally by work section
				return d3.descending(lookupIDTable.get(nodeA.work), lookupIDTable.get(nodeB.work));
			},
			align: "center",
			colors: authorColors,
			linkColor: "source",
			linkTitle: null
		}) :
	null

```


```js
// Create word-level Sankey chart for selected word

const wordSankey = wordIntxtNodes.length > 0 && wordIntxtEdges.length > 0 ? 
	SankeyChart({nodes: wordIntxtNodes, links: wordIntxtEdges, lookupIDTable: lookupIDTable},
		{
			sankeyType: "word",
			nodeLabel: d => lookupIDTable.get(d.id).word,
			rotateLabel: true,
			align: "center",
			nodeTitle: d => "",
			linkTitle: null,
			nodeSort: (a, b) => {
				let nodeA = lookupIDTable.get(a.id);
				let nodeB = lookupIDTable.get(b.id);
				let authorComp = d3.descending(lookupIDTable.get(nodeA.authorID),lookupIDTable.get(nodeB.authorID));
				let workComp = d3.descending(lookupIDTable.get(nodeA.workID),lookupIDTable.get(nodeB.workID));
				let workSegComp = d3.descending(lookupIDTable.get(nodeA.workSegID),lookupIDTable.get(nodeB.workSegID));
				let lineComp = d3.descending(nodeA.lineNum,nodeB.lineNum);
				if (authorComp !== 0) {return authorComp;}
				else if (workComp !== 0) {return workComp;}
				else if (workSegComp !== 0) {return workSegComp;}
				else {return lineComp;}
			}
			// by author, then work, then work section, then line
		}) :
	null

```




# Sandbox

Everything below here will not be in the final project.


## Working on intertexts networks



`wordsFiltered`
```js
wordsFiltered
```



`intertextsWordFiltered`
```js
intertextsWordFiltered
```

`wordIntxtNodes`
```js
wordIntxtNodes
```

`wordIntxtEdges`
```js
wordIntxtEdges
```

`wordSankey.nodes`
```js
wordSankey ? wordSankey.nodes : null
```
`wordSankey.links`
```js
wordSankey ? wordSankey.links : null
```

<hr>

## Data

<details>
<summary>Click here to view the full data.</summary>

Raw data from nodegoat (extracted into separate objects):

```js
nodegoatModel
```

Data after initial transformation:

`nodegoatTables`
```js
nodegoatTables
```
`meters`
```js
meters
```
`intertextsTable`
```js
intertextsTable
```

</details>

<hr>

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

