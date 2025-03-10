# Visualizing Intertextuality

A project to visualize intertexts in Latin poetry using [nodegoat](https://nodegoat.net/), [Observable Framework](https://observablehq.com/framework/), and Python.

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

```js
// Create authors dropdown

const authorList = [];
const authorTable = nodegoatTables.author_table;

for (let author in authorTable) {
	const authorSet = [authorTable[author].author_name, authorTable[author].obj_id];
	authorList.push(authorSet);
}


const authorPicker = Inputs.select(new Map([[null,null]].concat(authorList)), {label: "Author:", value: null, sort: true});
// const authorPicker = Inputs.select(new Map(authorList), {label: "Author:", sort: true});
let authorID = view(authorPicker);



/* This (suggested by ChatGPT) works to log the correct value, but it doesn't seem to pass outside of the async expression.

let selectedAuthorID;

(async () => {
  for await (const value of authorID) {
    selectedAuthorID = value;
    console.log("Updated Author ID:", selectedAuthorID);
  }
})();

*/

// Create works dropdown

const workList = [];
const workTable = nodegoatTables.work_table;


// VF id: '20215016'

for (let work in workTable) {
	if (workTable[work].author_id === authorID) {
		workList.push(workTable[work].title);
	}
}

const workPicker = Inputs.select([null].concat(workList), {label: "Work:"});


// Create work section dropdown

const workSecList = [];
const workSubSecList = [];
const workSegTable = nodegoatTables.work_seg_table;


// Create work subsection dropdown


// let test = authorID.valueOf();

```

```js
authorPicker
```
The author's ID is ${authorID}.
<!--
... ${test}
... ${authorID.valueOf()}
-->



```js
workPicker
```



### Selecting just VF intertexts manually, for now

```js

const VF_ID = '20215016';
const Arg_ID = '20215018';
const Arg2_ID = '20238544';

let workSegLineMin;
let workSegLineMax;
let workSegMeterID;

// Set variables for chart display

for (let workSeg in workSegTable) {
	if (workSegTable[workSeg].obj_id === Arg2_ID) {
		workSegLineMin = workSegTable[workSeg].first_line;
		workSegLineMax = workSegTable[workSeg].last_line;
		workSegMeterID = workSegTable[workSeg].meter_id;
	}
}
```

```js
// Create number pickers for range of lines to display

const lineMinPicker = Inputs.number([workSegLineMin, workSegLineMax], {step: 1, label: "Select starting line: ", placeholder: workSegLineMin});
const startLine = view(lineMinPicker);

const lineMaxPicker = Inputs.number([workSegLineMin, workSegLineMax], {step: 1, label: "Select ending line: ", placeholder: workSegLineMax});
const endLine = view(lineMaxPicker);


// Build words

const wordInstTable = nodegoatTables.word_instance_table;
const wordInstArr = [];

for (let inst in wordInstTable) {
	if (wordInstTable[inst].work_segment_id === Arg2_ID) {
		wordInstArr.push(wordInstTable[inst])
	}
}

const wordsFiltered = wordInstArr.filter(inst => inst.line_num >= 470 && inst.line_num <= 480);


// Get intertexts

const wordLvlIntxts = nodegoatTables.word_lvl_intxt_table;

for (let word in wordsFiltered) {
	wordsFiltered[word].directIntertexts = 0;
	wordsFiltered[word].indirectIntertexts = 0;
	
	const intxtIdArr = [];
	for (let intxt in wordLvlIntxts) {
		if (wordLvlIntxts[intxt].target_word_id == wordsFiltered[word].obj_id) {
			wordsFiltered[word].directIntertexts += 1;
			intxtIdArr.push(wordLvlIntxts[intxt].source_word_id);
		}
	}
	
	while (intxtIdArr.length > 0) {
		let id = intxtIdArr[0];
		for (let intxt in wordLvlIntxts) {
			if (wordLvlIntxts[intxt].target_word_id == id) {
				wordsFiltered[word].indirectIntertexts += 1;
				intxtIdArr.push(wordLvlIntxts[intxt].source_word_id);
			}
		}
		intxtIdArr.shift();
	}		
	
}

```

```js
wordsFiltered
```




### Create Grid

```js
// Define grid width.
let gridX;
const meter_id = workSegMeterID; // the value will depend on the selection's meter

for (let meter in meters) {
	if (meters[meter].meter_id === meter_id) {
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


### Testing stuff goes below here.

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


```js
let lineMin;
let lineMax;

lineMin = 1; // this will actually need to change depending on the range of the selection
lineMax = 10; // this will actually need to change depending on the range of the selection

const lineRange = [];

for (let i = lineMin; i <= lineMax; i++) {
	lineRange.push(i);
}
```

```js
lineRange
```

```js
const numX = workArr.length; // this will actually be determined by the appropriate length for a given meter
const numY = lineRange.length;
const cellSize = 20;
const gridHeight = numY * cellSize;
const gridWidth = numX * cellSize;
```

```js
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

```python
test_string = "hello world"
print(f"This is a Python test: {test_string}.")
```

```js
// Attach meters table for querying.
const meters = FileAttachment("data/meters.json").json()
```

```js
meters
```
