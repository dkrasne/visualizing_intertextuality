---
title: Visualizing Intertextuality
---

# Visualizing Intertextuality

A project to visualize intertexts in Latin poetry using [nodegoat](https://nodegoat.net/), [Observable Framework](https://observablehq.com/framework/), and Python. View the code on [GitHub](https://github.com/dkrasne/visualizing_intertextuality).


<!-- Load data -->

```js
const nodegoatModel = FileAttachment("data/nodegoat_data.json").json()
```


```js
const nodegoatTables = FileAttachment("data/nodegoat_tables.json").json()
```


## Select passage to view


```js
// Create authors dropdown

const authorList = [];
const authorTable = nodegoatTables.author_table;

for (let author in authorTable) {
	const authorSet = [authorTable[author].author_name, authorTable[author].obj_id];
	authorList.push(authorSet);
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
	if (!workSegTable[workSeg].work_subsection) {
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
const lineMaxPicker = Inputs.number([workSegVars.workSegLineMin, workSegVars.workSegLineMax], 
									{step: 1, 
									label: "Select ending line: ", 
									value: workSegVars.workSegLineMin + 19, 
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

// STILL NEED TO ADD LOGIC FOR ENDING PAST THE MAX AVAILABLE, AS WELL AS IF THE FIRST LINE ISN'T 1.
```

```js
// Establish metrical positions

const meterID = workSegVars.workSegMeterID;
let positions;
let meterLen;

for (let meter in meters) {
	if (meters[meter].meter_id === meterID) {
		positions = meters[meter].positions;
		meterLen = meters[meter].max_line_beats;
	}
}

const meterPosArr = d3.range(1, meterLen+1);

let i = 1;
for (let pos in positions) {
	const posBeats = positions[pos].pos_len;
	positions[pos].gridNums = [];
	for (let j = 0; j < posBeats; j++) {
		positions[pos].gridNums.push(i);
		i += 1;
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

const intertextsArr = intertextsArrComplete.filter(pos => pos.word);

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

// Define grid height.
const gridY = (lineRange.lastLine - lineRange.firstLine) + 1;

const cellSize = 15;
const gridHeight = gridY * cellSize;
const gridWidth = gridX * cellSize;
```

<!--
The grid will be ${gridX} cells wide.
The grid will be ${gridY} cells tall.
-->


```js

if (intertextsArr.every(intxt => intxt.intxtCnt === 0)) {
	display(html`<p>Based on information currently in the database, there are no intertexts in the specified passage.</p>`)
} else {

display(

html`<div class="grid grid-cols-2"><div class="card" style="background-color:#ccccff; padding-top: 30px;">

<h2 style="padding-bottom: 10px;">${passageDetails.authorName}, <i>${passageDetails.workTitle}</i>, ${passageDetails.workSegName}: lines ${lineRange.firstLine}&ndash;${lineRange.lastLine}</h2>

${Plot.plot({
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
//		padding: 0,
		tickSize: 0,
		},
	color: {scheme: "Greens", 
		legend: true, 
		label: "Total Intertexts",
//		ticks: d3.range(4)		// NEED TO SET THIS TO A RANGE FROM MIN. INTERTEXTS TO MAX. INTERTEXTS
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
/*				intxtCnt: {
					value: "intxtCnt",
					label: "# direct and indirect intertexts"
				}, */
			},
		})
	],
	style: {fontSize: "12px"},
	width: gridWidth + 100,
	height: gridHeight + 50,
	marginTop: 20,
	marginRight: 50,
	marginBottom: 30,
	marginLeft: 50
})}
</div>
<div><p>Eventually the text of the selected passage may go here, but it's more likely that I'll put a network visualization here.</p></div>
</div>`

)}
```

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


```js
// Attach meters table for querying.
const meters = FileAttachment("data/meters.json").json()
```

```js
meters
```
