# Visualizing Intertextuality

A project to visualize intertexts in Latin poetry using [nodegoat](https://nodegoat.net/), [Observable Framework](https://observablehq.com/framework/), and Python. View the code on [GitHub](https://github.com/dkrasne/visualizing_intertextuality).

## Prelims

### Load data

```js
const nodegoatModel = FileAttachment("data/nodegoat_data.json").json()
```

```js
nodegoatModel
```

```js
const nodegoatTables = FileAttachment("data/nodegoat_tables.json").json()
```

```js
nodegoatTables
```

### Select work section to view

```js
// Create authors dropdown

const authorList = [];
const authorTable = nodegoatTables.author_table;

for (let author in authorTable) {
	const authorSet = [authorTable[author].author_name, authorTable[author].obj_id];
	authorList.push(authorSet);
}

const authorPicker = Inputs.select(new Map([[null,null]].concat(authorList)), {label: "Author:", value: null, sort: true});
let authorID = view(authorPicker);
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

const workPicker = Inputs.select(new Map([[null, null]].concat(workList)), {label: "Work:", value: null, sort: true});
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

const workSegPicker = Inputs.select(new Map([[null, null]].concat(workSegList)), {label: "Work section:", value: null, sort: true});
const workSegID = view(workSegPicker);
```


```js
authorPicker
```
<!--
The author's ID is ${authorID}.
-->

```js
workPicker
```

```js
workSegPicker
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

// Create number pickers for range of lines to display

const lineMinPicker = Inputs.number([workSegVars.workSegLineMin, workSegVars.workSegLineMax], 
									{step: 1, 
									label: "Select starting line: ", 
									value: workSegVars.workSegLineMin, 
									default: workSegVars.workSegLineMin});
const startLine = view(lineMinPicker);

const lineMaxPicker = Inputs.number([workSegVars.workSegLineMin, workSegVars.workSegLineMax], 
									{step: 1, 
									label: "Select ending line: ", 
									value: workSegVars.workSegLineMin + 19, 
									default: workSegVars.workSegLineMax});
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
} else {lineRange.lastLine = lineRange.firstLine + 20;}
```

```js
// Establish metrical positions

const meterID = workSegVars.workSegMeterID;
let positions;

for (let meter in meters) {
	if (meters[meter].meter_id === meterID) {
		positions = meters[meter].positions;
	}
}

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

```js
positions
```

## Prepare intertexts

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
```

```js
// Get intertexts

const wordLvlIntxts = nodegoatTables.word_lvl_intxt_table;

for (let word in wordsFiltered) {
	wordsFiltered[word].directIntertexts = 0;
	wordsFiltered[word].indirectIntertexts = 0;
	wordsFiltered[word].directIntertextIDs = [];
	wordsFiltered[word].indirectIntertextIDs = [];

// Gather direct intertexts
	
	for (let intxt in wordLvlIntxts) {
		if (wordLvlIntxts[intxt].target_word_id === wordsFiltered[word].obj_id) {
			let sourceID = wordLvlIntxts[intxt].source_word_id;
			wordsFiltered[word].directIntertexts += 1;
			wordsFiltered[word].directIntertextIDs.push(sourceID);
		}
	}

// Gather indirect intertexts based on direct intertexts

	const checkedIDs = [];
	for (let i in wordsFiltered[word].directIntertextIDs) {
		let id = wordsFiltered[word].directIntertextIDs[i];
		for (let intxt in wordLvlIntxts) {
			if (wordLvlIntxts[intxt].target_word_id === id) {
				let sourceID = wordLvlIntxts[intxt].source_word_id;	
				if (!wordsFiltered[word].indirectIntertextIDs.includes(sourceID) && !wordsFiltered[word].directIntertextIDs.includes(sourceID)) {
					wordsFiltered[word].indirectIntertextIDs.push(sourceID);
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

}
	

```

```js
wordsFiltered
```


```js

```


## Create Grid

```js
// Define grid width based on the selection's meter.

let gridX;

for (let meter in meters) {
	if (meters[meter].meter_id === meterID) {
		gridX = meters[meter].max_line_beats
	}
}

// Define grid height.
const gridY = (endLine - startLine) + 1;

```

The grid will be ${gridX} cells wide.
The grid will be ${gridY} cells tall.

```js
Plot.plot({
	grid: true,
	x: {label: 'Position', domain: d3.range(1,gridX+1)},
	y: {label: 'Line', domain: d3.range(startLine, endLine +1)},
	color: {scheme: "Blues"},
})
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
