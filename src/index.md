---
title: Visualizing Intertextuality
theme: [air, wide]
toc: false
---

# Visualizing Intertextuality

**Developed by:** [Darcy Krasne](http://www.darcykrasne.com/)

[See the About page](./about) for an explanation of this project.

*N.B. As Observable is phasing out its cloud hosting, this site has relocated to http://dkrasne.github.io/visualizing_intertextuality. Please take note of the new address.*

<!-- Probably make a 'Statistics' or 'Fun facts' box here, to the right, or on the About page -->

Number of words of Latin poetry (or its antecedents) currently in the database: **${nodegoatTables.word_instance_table.length}**

## Select passage to view

<div class="tip">Currently there is a limited set of intertexts in the database. Choose Valerius Flaccus, <i>Argonautica</i>, Book 1, lines 1&ndash;4 or Book 2, lines 475&ndash;476 to see the display of some richly intertextual passages. You can also <a href="./sankey">view this diagram</a> to see the complete network of intertexts currently in the database.</div>

<!-- Author, Work, and Work Section Selectors -->

<div class="grid grid-cols-3">
	<div class="card">${authorPicker}</div>
	<div class="card">${workPicker}</div>
	<div class="card">${workSegPicker}</div>
</div>

<!-- Starting and Ending Line Selectors -->

<div class="grid grid-cols-2">
	<div class="card">${lineMinPicker}</div>
	<div class="card">${lineMaxPicker}</div>
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
	<div class="card" style="background-color:${bgColor}; padding: 20px 20px 0 20px;">

		<h2 style="padding-bottom: 10px; font-size:large;">${passageDetails.authorName ? `${passageDetails.authorName}, `: ""}<i>${passageDetails.workTitle}</i>${passageDetails.workSegName ? `, ${passageDetails.workSegName}` : ""}: lines ${lineRange.firstLine}&ndash;${lineRange.lastLine}</h2>

		${readingWords.selected.length > 0 ? // show reading alternatives, if they exist for the passage
			display(
				html`
				<p>Choose the reading(s) that will appear in the specified line(s):</p>
				${altWordSelectorSet}
				<hr>
				`
			) : null
		}


		${plotDisplay}

		${removedMonosyllables.length > 0 ? display(
			html`
			<p style="max-width:none; font-size:smaller;">N.B. ${removedMonosyllables.length} elided ${removedMonosyllables.length === 1 ? 'monosyllable' : 'monosyllables'} ${removedMonosyllables.length === 1 ? 'is' : 'are'} not shown above: elided monosyllables are only shown when the word following them either is itself not in the database or has no intertexts in the database.</p>
			`
		) : null}

	</div>

	<div>
		<h4>How to use this chart</h4>
		<p style="font-size:smaller;">Mouse over a cell to see a popup that shows what word it represents and how many direct and indirect intertexts it has; click on a cell to freeze the popup information. Mousing over or clicking on a cell will also display a visualization below of that word&rsquo;s intertextual lineage.</p>
		
		<p style="font-size:smaller;"><b>Direct intertexts</b> are those where a scholar has suggested a direct link between the present word and a word in an earlier text. <b>Indirect intertexts</b> are intertexts at further remove (i.e., where a direct or indirect intertext refers to another, still earlier, passage). Currently, the project does not include intratexts (allusions to other passages within the same text).</p>

		<p style="font-size:smaller;">A <b>missing</b> word (represented as a gap) is not currently in the database. A word shown with <b>zero total intertexts</b> is either in the database only as the ancestor of another word, or has not yet been assigned to any intertextual relationships.</p>

		<p style="font-size:smaller;"><b>Two caveats:</b> absence of a word does not necessarily mean that there are no intertexts, just that they are not yet in the database; and lines appear in numeric order, even if editors agree that they should be transposed.</p>

		<p style="font-size:smaller;">For a fuller explanation of the data and its representation, see <a href="./about">the About page</a>.</p>
	</div>
</div>

<div class="grid grid-cols-2" style="margin-top: 2em;">
	<div>
		${
			display(html`
			<h4>The intertextual ancestry of the selected passage</h4>
			<p style="font-size:smaller;">Mouse over a rectangular node to see the work and section that it represents. Mouse over a linking flow path to see the word(s) it represents.</p>
			<p style="font-size:smaller;">A full explanation of how to read this visualization can be found on <a href="./sankey">the Full Intertext Diagram page</a>.</p>
			${display(sectionSankey)}`)
		}
	</div>
	<div>
		${!plotCurrSelect ? 
		display(html`
			<p style="border: 2px solid black; padding: 1em;"><i>Mouse over a word in the passage display density chart above in order to see the lineage for that particular word. (Click on the word to freeze the display.)</i></p>
		`) :
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

<div>

## References

*To view the references for all the passage&rsquo;s intertexts, tick the following box; otherwise, only references for a selected word&rsquo;s intertextual lineage will be displayed.*

```js
const refAll = view(Inputs.toggle({label: "View all?"}))
```

<ul style="max-width:none" id="references">
<!-- the references list will show up here -->
</ul>

<p style="font-size: smaller">
N.B. Every intertext in the database has <b>at least one</b> publication entered as a source. Many other, unlisted publications may record the same intertext; there is no attempt at completion, nor any effort to cite the *first* publication to record a given intertext.
</p>

</div>

<!-- ```js
if (!plotDisplay) {display(html`<p></p>`)}
else {
	display(html`<p>The selected datapoint, which will serve as the starting point of the generated network (this will eventually not be displayed):</p>`)
	if (plotCurrSelect) {display(plotCurrSelect)} else {display(html`<p><i>No current selection in plot.</i></p>`)}
	}
``` -->

<hr>


<!-- DATA LOADING AND MANIPULATION; VISUALIZATION CREATION -->


<!-- Load data -->

```js
import {createLookupIDTable, authorColors, proseID, deepCopy} from './js/global_constants.js';
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
// Attach list of modified intertexts for alternative textual readings
const intertextsModTable = FileAttachment("data/intxts_full_modified.json").json()
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

// filter to authors that have written poetry in plottable meters
let workSegFilter = nodegoatTables.work_seg_table.filter(workSeg => workSeg.meter_id !== proseID).map(workSeg => workSeg.work_id);
let workFilter = nodegoatTables.work_table.filter(work => workSegFilter.includes(work.obj_id)).map(work => work.author_id);

let authorFilter = nodegoatTables.author_table.filter(author => workFilter.includes(author.obj_id));


for (let author in authorFilter) {
	if (authorFilter[author].language === "Latin") {
		const authorSet = [authorFilter[author].author_name, authorFilter[author].obj_id];
		authorList.push(authorSet);
	}
}

// Add catch-all for works without an assigned author
authorList.push(["Anonymous works", "000"]);

authorList.sort((a,b) => d3.ascending(a[0], b[0]));

const authorPicker = Inputs.select(new Map([[null,null]].concat(authorList)), {label: "Select author:", value: null, sort: false});
const authorID = view(authorPicker);
```

```js
// Create works dropdown

const workList = [];
const workTable = nodegoatTables.work_table;

for (let work in workTable) {

	if ((workTable[work].author_id === authorID && workTable[work].author_id) || (authorID === "000" && !workTable[work].author_id)) {
		const workSet = [workTable[work].title, workTable[work].obj_id]
		workList.push(workSet);
	}
	
	// if an anonymous work is traditionally (but probably incorrectly) attributed to an author, also add it to their list of works, but with the title in brackets
	else if (workTable[work].authorship_prob_ids) {
		let altAuthorPossibilities = workTable[work].authorship_prob_ids.filter(problem => problem.refid === "21843").map(alt => alt.refval);
		
		if (altAuthorPossibilities.includes(authorID)) {
			const workSet = [`[${workTable[work].title}]`, workTable[work].obj_id]
			workList.push(workSet);
		}
	}

}

workList.sort((a,b) => d3.ascending(a[0], b[0]));

const workPicker = Inputs.select(new Map([[null, null]].concat(workList)), {label: "Select work:", value: null, sort: false});
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
		workSegList.push(workSegSet)
	}
}

workSegList.sort((a,b) => a[0].localeCompare(b[0], undefined, {numeric: true}));

const workSegPicker = Inputs.select(new Map([[null, null]].concat(workSegList)), {label: "Select work section:", value: null, sort: false});
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
		if (workTable[work].author_id !== authorID) {passageDetails.authorName = "";}
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
let schemeNumLines;

for (let m in meters) {
    let meterScheme = meters[m];
	if (meterScheme.metrical_scheme_id === meterID) {
        for (let n in meterScheme.components){
            let lineMeter = meterScheme.components[n];
            positions = n == 0 ? lineMeter.positions : positions.concat(lineMeter.positions);
            }
		meterLen = meterScheme.max_line_beats;
		linePattern = meterScheme.recur_line_pattern ? meterScheme.recur_line_pattern : schemeNumLines = meterScheme.components.length;
	}
}

const meterPosArr = d3.range(1, meterLen+1);
let linePatternArr = d3.range(1,linePattern+1);

let i = 1;
	for (let pos in positions) {
        if (positions[pos].position === "1a") {i = 1}
		const posBeats = positions[pos].pos_len;
		positions[pos].gridNums = [];
        let lineMeter = nodegoatTables.meter_pos_len_table.filter(mpos => mpos.obj_id === positions[pos].meter_pos_len_id)[0].meter_id;
        positions[pos].lineMeter = lineMeter;
		for (let j = 0; j < posBeats; j++) {
			positions[pos].gridNums.push(i);
            i += 1;
		}
	}

```

<!-- Prepare alternate word selectors -->

```js
const textProbTable = nodegoatTables.textual_prob_table;
const altReadTable = nodegoatTables.alternate_reading_table;

const textProbs = textProbTable.filter(textProb => textProb.work_segment_id === workSegID && textProb.line_num >= lineRange.firstLine && textProb.line_num <= lineRange.lastLine);
let textProbIDs = textProbs.map(textProb => textProb.obj_id);

const altWords = [];
const altWordSelectors = {};

if (textProbIDs.length > 0) {
	for (let id of textProbIDs) {
		let possReadings = altReadTable.filter(reading => reading.textual_prob_id === id);

		let textProb = textProbs.filter(prob => prob.obj_id === id)[0];

		for (let reading of possReadings) {
			let wordList = JSON.parse(JSON.stringify(reading.word_inst_ids));
			for (let i in wordList) {
				wordList[i] = lookupIDTable.get(wordList[i]);
			}
			wordList.sort((a,b) => d3.sort(a.startPos, b.startPos));
			let wordListString = wordList.map(word => word.word).join(", ");

			let startPosFirst = wordList.map(word => word.startPos)[0];
			let endPosLast = wordList.map(word => word.endPos)[wordList.length - 1];

			textProb["posRange"] = [startPosFirst, endPosLast];

			let altWordObj = {textProbID: id, readingID: reading.obj_id, wordIDs: reading.word_inst_ids, words: wordListString, line: textProb.line_num, default: reading.default_reading, active: false};

			reading.default_reading ? altWords.splice(0, 0, altWordObj) : altWords.push(altWordObj);
		}

		altWordSelectors[id] = Inputs.select(
			new Map(altWords.map(reading => [reading.words, reading.readingID])),
			{value: altWords.filter(reading => reading.default)[0].readingID,
				label: `line ${textProb.line_num}, positions ${textProb.posRange[0]} to ${textProb.posRange[1]}`, 
				sort: true	// if I don't sort, the default reading will be at the top of the list, but the rest won't be alphabetized
			}
		);
	}
}

const altWordSelectorSet = Inputs.form(altWordSelectors);
const altWordSelections = view(altWordSelectorSet);

```

```js
// the result of the selections will be a dictionary where the key is the textual problem ID and the value is the alternate reading option ID. These are both contained within the objects of the altWords array.

// for the selected reading in each selector, set the `active` property of that reading to `true`.

altWords.forEach(word => {
	if (Object.values(altWordSelections).includes(word.readingID)) {
		return word.active = true
	} else {
		return word.active = false}
	})


// anything else involving the active altWords readings needs to be INSIDE THIS CELL

// create an object with the array of possible readings, and the array of chosen readings
const readingWords = {
	possible: altWords.flatMap(reading => reading.wordIDs), 
	selected: altWords.filter(reading => reading.active).flatMap(reading => reading.wordIDs)
	};

const intxtModsTable = nodegoatTables.word_lvl_intxt_mod_table;

const intxtMods = [];

for (let wordID of readingWords.selected) { // for every word that has changed
	let intxtModsFilter = intxtModsTable.filter(intxt => intxt.wd_sub_id === wordID); // get all intexts that have that word as a substitute word
	if (intxtModsFilter.length > 0) {
		for (let intxtMod of intxtModsFilter){	// for every one of those modified intertexts
			// the old intertext is the one that the modifier will modify
			let oldIntxt = nodegoatTables.word_lvl_intxt_table.filter(oldIntxt => oldIntxt.obj_id === intxtMod.wd_lvl_intxt_id)[0];
			// make a clone of it
			let newIntxt = JSON.parse(JSON.stringify(oldIntxt));
			// give the modified intertext a new object ID
			newIntxt.obj_id = intxtMod.obj_id;
			// substitute the relevant word of the modified intertext
			for (let key in newIntxt) {
				if ((key === 'source_word_id' || key === 'target_word_id') && newIntxt[key] === intxtMod.wd_to_replace_id) {

					newIntxt[key] = intxtMod.wd_sub_id;
				}
			}
			// adjust the match types, as necessary
			for (let matchType of intxtMod.match_type_remove_ids) {
				if (newIntxt.match_type_ids.includes(matchType)) {
					let i = newIntxt.match_type_ids.indexOf(matchType);
					newIntxt.match_type_ids.splice(i, 1);
				}
			}
			for (let matchType of intxtMod.match_type_add_ids) {
				newIntxt.match_type_ids.push(matchType);
			}

			if (nodegoatTables.word_lvl_intxt_table.filter(intxt => intxt.obj_id === newIntxt.obj_id).length === 0){nodegoatTables.word_lvl_intxt_table.push(newIntxt)};
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
		// add all words in the work segment that *either* aren't in a textual problem spot at all *or* are the selected words for the textual problem
		if (!readingWords.possible.includes(wordInstTable[inst].obj_id) || readingWords.selected.includes(wordInstTable[inst].obj_id))
		{
			wordInstArr.push(wordInstTable[inst])
		}
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
const extraNumericalLineWords = [];

for (let line in lineArr) {
    let lineMeter;
    if (wordsFiltered.filter(word => word.line_num === lineArr[line]).length > 0) {
        let wordStart = wordsFiltered.filter(word => word.line_num === lineArr[line])[0].start_pos_id;
        lineMeter = nodegoatTables.meter_pos_len_table.filter(pos => pos.obj_id === wordStart)[0].meter_id;
        }
	for (let i in meterPosArr) {
		let intertextObj = {};
		intertextObj.lineNum = lineArr[line];
		intertextObj.linePos = meterPosArr[i];
		intertextObj.intxtCnt = 0;
		for (let posn in positions) {
			if (positions[posn].gridNums.includes(meterPosArr[i]) && positions[posn].lineMeter === lineMeter) {
				intertextObj.linePosID = positions[posn].meter_pos_len_id;
				break;
			}
		}
		for (let word in wordsFiltered) {
			if (wordsFiltered[word].line_num === intertextObj.lineNum && wordsFiltered[word].posIDs.includes(intertextObj.linePosID)) {
				if (!wordsFiltered[word].line_num_modifier) {
					intertextObj.wordObj = wordsFiltered[word];
					intertextObj.intxtCnt = wordsFiltered[word].directIntertexts + wordsFiltered[word].indirectIntertexts;
					intertextObj.word = wordsFiltered[word].word;
				} else {	// make a separate object for words in an extranumerical line, otherwise they overwrite the same positions in the regular line
					let extraIntertextObj = JSON.parse(JSON.stringify(intertextObj));
					extraIntertextObj.lineNum = `${wordsFiltered[word].line_num}${wordsFiltered[word].line_num_modifier}`;
					extraIntertextObj.wordObj = wordsFiltered[word];
					extraIntertextObj.intxtCnt = wordsFiltered[word].directIntertexts + wordsFiltered[word].indirectIntertexts;
					extraIntertextObj.word = wordsFiltered[word].word;
					extraNumericalLineWords.push(extraIntertextObj);
				}
			}
		}
		
		intertextsArrComplete.push(intertextObj);
	}
}

const intertextsArr = intertextsArrComplete.filter(pos => pos.word)	// only include cells that have a word assigned to them
											.concat(extraNumericalLineWords);	// add cells from extranumerical line array

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
	if (meters[meter].metrical_scheme_id === meterID) {
		gridX = meters[meter].max_line_beats;
	}
}

// Define grid height based on number of lines.

let gridYInterim = (lineRange.lastLine - lineRange.firstLine) + 1;
let extraLineSet;

// make a set of any extranumerical lines

if (wordsFiltered.filter(word => word.line_num_modifier).length > 0) {
	extraLineSet = new Set(
		wordsFiltered.filter(word => word.line_num_modifier)
					.map(word => ({lineNum: word.line_num, lineNumMod: word.line_num_modifier, lineNumString: `${word.line_num}${word.line_num_modifier}`}))
	);
	gridYInterim += extraLineSet.size;	// if there are extranumerical lines, increase the height multiplier accordingly, so that cells remain square
}

const extraLines = extraLineSet ? Array.from(extraLineSet) : [];

const gridY = gridYInterim;

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

// set tick range; increase step every ten (max) intertexts
let step;
if (d3.max(intxtCnts)%10 === 0) {
	step = d3.max(intxtCnts)/10;
}
else {
	step = Math.floor(d3.max(intxtCnts)/10) + 1;
};
let tickRange = d3.range(Math.min(...intxtCnts), Math.max(...intxtCnts)+1, step);

let lineVals = d3.range(lineRange.firstLine, lineRange.lastLine +1);

// if there are extranumerical lines, insert them into the line values array

for (let line of extraLines) {
	let insertAfter = line.lineNum;
	let insertAfterIndex = lineVals.indexOf(insertAfter) + 1;
	let insertString = line.lineNumString;
	lineVals.splice(insertAfterIndex, 0, insertString);
}


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
		// domain: d3.range(lineRange.firstLine, lineRange.lastLine +1),
		domain: lineVals,
		tickSize: 0,
		},
	color: {scheme: "Greens", 
		legend: true, 
		label: "Total Intertexts (direct & indirect)",
		ticks: tickRange,
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
		Array.from(new Set(wordsFiltered.concat(removedMonosyllables).map(word => word.directIntertextIDs.concat(word.indirectIntertextIDs)).flat())) : 
		[];

// Filter the full table of intertexts to just those that include the relevant words
const intertextsTableCopy = deepCopy(intertextsTable).concat(deepCopy(intertextsModTable));
let passageIntxts = intertextsTableCopy.filter(intxt => passageWordIntxts.includes(intxt.source_word_id) || passageWordIntxts.includes(intxt.target_word_id));

// Get the IDs for those intertexts, both the word-level intertext IDs and the word-level intertext group IDs
const intxtIDs = passageIntxts.map(intxt => [intxt.intxt_grp_id, intxt.intxt_id]).flat().filter(id => id !== null);
const passageIntxtIDs = passageIntxts.map(intxt => intxt.intxt_id);


// FILTER SANKEY DATA //

// Filter the work-segment edges based on those intertexts
let sankeyEdges = deepCopy(sankeyData.edges); // prevents the filtering from affecting the actual data

let sankeyFilteredEdgesArr = sankeyEdges.filter(edge => intxtIDs.includes(edge.id));

// If any intertext words are in a textual problem, then adjust Sankey based on the selected word(s).
// THIS WILL NEED TO BE MODIFIED FURTHER IF/WHEN THERE ARE REPLACEMENT WORDS POINTING TO A DIFFERENT PASSAGE
// ALTERNATIVELY, AT THAT POINT I SHOULD SHIFT THE SANKEY BUILDING FROM THE PYTHON DATALOADER INTO A JS FUNCTION
for (let edge of sankeyFilteredEdgesArr) {
	for (let wordSet of ["source_words", "target_words"]) {
		for (let i in edge[wordSet]) {
			let focusWord = edge[wordSet][i]
			if (readingWords.possible.includes(focusWord)) {
				let altWordsFocus = altWords.filter(reading => reading.wordIDs.includes(focusWord))[0];
				if (altWordsFocus.active == false) {
					let oldWords = altWordsFocus.wordIDs;
					let altWordsReplacement = altWords.filter(reading => reading.active == true)[0];
					let newWords = altWordsReplacement.wordIDs;
					for (let word of oldWords) {
						let iWord = edge[wordSet].indexOf(word);
						edge[wordSet].splice(iWord, 1);
					}
					for (let word of newWords) {
						edge[wordSet].push(word);
					}
				}
			}
		}
	}
}

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

const wordSankeyIntxtIDs = [];

let currWordId;
let ancestorWordIDs = [];
let descendantWordIDs = [];

if (plotCurrSelect) {
	
	currWordId = plotCurrSelect.wordObj.obj_id;	// set current word ID to the selected word

	let intertextsTableExtended = intertextsTable.concat(intertextsModTable);

	// create functions for getting a word's immediate ancestors or descendants
	function getWordAncestors(currWordId){
		for (let i in intertextsTableExtended) {
			let intxt = intertextsTableExtended[i];
			// for each intertext in the intertexts table, if its target ID matches the focus word (either the selected word or one of its ancestors), add it to the list of ancestor intertexts and add its source to the list of words to be processed.
			if (currWordId === intxt.target_word_id) {
				ancestorIntertexts.push(intxt);
				ancestorWordIDs.push(intxt.source_word_id);
				wordSankeyIntxtIDs.push(intxt.intxt_id);
			}
		}
	}
	function getWordDescendants(currWordId){
		for (let i in intertextsTableExtended) {
			let intxt = intertextsTableExtended[i];
			// for each intertext in the intertexts table, if its source ID matches the focus word (either the selected word or one of its descendants), add it to the list of descendant intertexts and add its target to the list of words to be processed.
			if (currWordId === intxt.source_word_id) {
				descendantIntertexts.push(intxt);
				descendantWordIDs.push(intxt.target_word_id);
				wordSankeyIntxtIDs.push(intxt.intxt_id);
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
			nodeGroup: d => {
				if (!d.author) {return lookupIDTable.get(d.id).workID} // this should enable coloring of anonymous works by the work itself
				return d.author
				},
			nodeLabel: d => {
							let nodesFilter = nodes.filter(node => node.id === d.id);
							let nodeAuthorID;
							for (let n in nodesFilter) {nodeAuthorID = nodesFilter[n].author}
							return lookupIDTable.get(nodeAuthorID);
							},
			nodeTitle: null,
			nodeSort: (a,b) => {
				let nodeA = sankeyData.nodes.find(work => work.name === a.id);
				let nodeB = sankeyData.nodes.find(work => work.name === b.id);
				// Sort so that authors go A-Z left-to-right (= bottom-to-top); d3.descending returns -1, 0, or 1
				let authorA = nodeA.author ? lookupIDTable.get(nodeA.author) : "anonymous";
		        let authorB = nodeB.author ? lookupIDTable.get(nodeB.author) : "anonymous";
				if (authorA === "anonymous") {
					authorA += d3.descending(lookupIDTable.get(nodeA.work).workTitle)
				}
				if (authorB === "anonymous") {
					authorB += d3.descending(lookupIDTable.get(nodeB.work).workTitle)
				}
				let authorComp = d3.descending(authorA.toLowerCase(), authorB.toLowerCase());
				// Within authors, sort so that all work sections are in order by work
				let workComp = d3.descending(lookupIDTable.get(nodeA.work).workTitle, lookupIDTable.get(nodeB.work).workTitle);
				let workSegComp = lookupIDTable.get(b.id).section.localeCompare(lookupIDTable.get(a.id).section, undefined, {numeric: true});
				if (authorComp !== 0) return authorComp; // if the authors aren't the same, don't go any further in sorting
				if (workComp !== 0) return workComp;
				return workSegComp; // sort by work section
			},
			align: "center",
			colors: authorColors,
			linkColor: "source",
			linkTitle: null
		}) :
	undefined

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
			nodeTitle: null,
			linkTitle: null,
			nodeSort: (a, b) => {
				let nodeA = lookupIDTable.get(a.id);
				let nodeB = lookupIDTable.get(b.id);
				let authorComp = d3.descending(lookupIDTable.get(nodeA.authorID),lookupIDTable.get(nodeB.authorID));
				let workComp = d3.descending(lookupIDTable.get(nodeA.workID),lookupIDTable.get(nodeB.workID));
				let workSegComp = lookupIDTable.get(nodeB.workSegID).section.localeCompare(lookupIDTable.get(nodeA.workSegID).section, undefined, {numeric: true});
				//let workSegComp = d3.descending(lookupIDTable.get(nodeA.workSegID).section,lookupIDTable.get(nodeB.workSegID).section);
				let lineComp = d3.descending(nodeA.lineNum,nodeB.lineNum);
				if (authorComp !== 0) {return authorComp;}
				else if (workComp !== 0) {return workComp;}
				else if (workSegComp !== 0) {return workSegComp;}
				else {return lineComp;}
			}
			// by author, then work, then work section, then line
		}) :
	undefined

```

<!-- Create references list -->

```js
let refChoice = refAll ? passageIntxtIDs.concat(wordSankeyIntxtIDs) : wordSankeyIntxtIDs;
let intxtIdSet = new Set(refChoice);
let sourcesFiltered = nodegoatTables.sources_table.filter(intxt => intxtIdSet.has(intxt.obj_id))
let sourcesFilteredIDs = Array.from(new Set(sourcesFiltered.map(item => item.source_id)))
//console.log(lookupIDTable.get(sourcesFilteredIDs[0]))

const sourcesArray = []

for (let i in sourcesFilteredIDs) {
	let sourceID = sourcesFilteredIDs[i];
	let sourceDict = {};

	let source = sourcesFiltered.filter(source => source.source_id === sourceID);

	let sourceLocs = source.map(source => source.source_location);
	sourceLocs = Array.from(new Set(sourceLocs));

	sourceDict['sourceID'] = sourceID;
	sourceDict['sourceLocs'] = sourceLocs.sort((a, b) => a.localeCompare(b, undefined, {numeric: true}));

	sourcesArray.push(sourceDict);

}

// console.log(sourcesArray);
// console.log(lookupIDTable.get("20308257"))

const pubList = []

for (let i in sourcesFilteredIDs) {
	let pub = lookupIDTable.get(sourcesFilteredIDs[i]);
	let pubString = '';

	// ancient sources
	if (pub.authorID) {
		let author = lookupIDTable.get(pub.authorID); 
		pubString = author;
		let workTitle = pub.workTitle;
		pubString += `, <i>${workTitle}</i>`
	}

	// modern sources
	else {
	// add author(s), separated by comma if more than one
	for (let i in pub.authorIDs) {
		pubString += i > 0 ? ', ' : '';
		let author = lookupIDTable.get(pub.authorIDs[i]);
		pubString += author;
	}

	// add publication date
	pubString += ` (${pub.pubDate}) `;

	// add article/chapter title if there is one
	pubString += pub.articleChapterTitle ? `&ldquo;${pub.articleChapterTitle},&rdquo; ` : ''
	
	// add book/journal title
	pubString += `<i>${pub.bookJournalTitle}</i>`

	// add journal issue number if there is one
	pubString += pub.issueNumber ? ` ${pub.issueNumber}` : ''
}

	// get citation locations for source and add them
	let sourceLocs = sourcesArray.filter(source => source.sourceID === sourcesFilteredIDs[i])[0].sourceLocs.filter(loc => loc !== '');
	sourceLocs = sourceLocs.length > 0 ? sourceLocs.join(', ') : ''
	pubString += sourceLocs ? `: ${sourceLocs}.` : '.'

	pubList.push(pubString);

	
}


// const htmlTest = pubList.sort().map(item => html`<li>${item}</li>`);

// let textString = "<i>this is italics</i> and this is not <b>but this is bold</b> &ldquo;&rdquo;"
```

```js
const refDiv = d3.select("ul#references");

refDiv.selectAll("li").data(pubList.sort()).join("li").join("text").html(d => d);

```

<!-- 
```js
display(html`<ul>${htmlTest}</ul>`)
```
 -->


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

