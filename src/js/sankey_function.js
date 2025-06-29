//create customized SankeyChart() function
// ORIGINAL VERSION:
// Copyright 2021-2023 Observable, Inc.
// Released under the ISC license.
// https://observablehq.com/@d3/sankey-diagram


import * as d3Sankey from "npm:d3-sankey@0.12.3";
import * as d3 from "npm:d3";
import {proseID} from "./global_constants.js";

function SankeyChart(
  {
    nodes, // an iterable of node objects (typically [{id}, …]); implied by links if missing
    links, // an iterable of link objects (typically [{source, target}, …])
    lookupIDTable
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
    marginLeft = 1, // left margin, in pixels
    sankeyType = "passage", // passage or word
    rotateLabel = false, // should the node label be parallel to the node?
    nodeDrag = false, // should the nodes be repositionable?
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

//  const svg = d3
const svg_outer = d3
    .create("svg")
    .attr("width", width)
    .attr("height", width)
    .attr("viewBox", [0, 0, width, width])
    .attr("style", "max-width: 100%; height: auto; height: intrinsic; overflow: visible")
//    .attr("transform", "rotate(90,0,0) translate("+marginTop+",0)")
//    .attr("style","border: 1px solid black")
    ;

  const svg = svg_outer.append("g")
    .attr("transform", "rotate(90,0,0) translate(0,-"+(width*.75 + marginTop)+")")
    .attr("id","outer_group")



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
        .attr("opacity","0.6")
        .attr("class", "node-box");


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

// const svgSelect = d3.select(svg);

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



// add pop-up tooltips to links

const tooltipLinks = svg
  .append("g")
    .attr("class", "tooltip")
    .attr("transform", "rotate(-90,0,0) translate(50,-10)")
    .attr("opacity", "0")
    ;

const tooltipLinksBox = tooltipLinks
    .append("rect")
//      .attr("height", "50")
//      .attr("width", "140")
      .attr("stroke","black")
      .attr("fill","white")
      .attr("filter","drop-shadow(0 3px 4px rgba(0,0,0,.5))");
  

  linkPathGPath
        .on("mouseenter", function (e,d) {
            const tooltipLinksText = tooltipLinks
              .append("text")
                .attr("class", "tooltip-link-text")
                .attr("x","5")
                .attr("y",".5em")
                .attr("font-size","15")
                .attr("font-family","sans-serif")
                .attr("font-weight","normal")
                .attr("stroke","none")
                .attr("fill","black");

            // set x and y based on location of where mouse enters the link
            // Pointer(X,Y) is based on the unrotated X/Y (so opposites); max X is ~620, max Y is ~400 in both the smaller and larger viz            
            let [y,x] = d3.pointer(e, this);

            tooltipLinks
              .attr("transform", `rotate(-90,0,0) translate(${(x*-1)+20},${(y+20)})`)
              .attr("opacity", "1")
              ;

            if (sankeyType === "word") {
              let matchTypeIDs = origLinks.filter(edge => edge.source === d.source.id && edge.target === d.target.id)[0].matchTypes;
              let matchTypes = [];
              for (let i in matchTypeIDs) {
                let mt = lookupIDTable.get(matchTypeIDs[i]);
                matchTypes.push(mt);
                let textrow = tooltipLinksText
                  .append("tspan")
                    .attr("x", "5")
                    .attr("dy", "1em")
                    .attr("class", "tooltip-link-text-line");
                textrow.text(`\u2022 ${mt}`);
                }
              }

            if (sankeyType === "passage") {
              // List words by line
              let sourceNode = d.source.id;
              let targetNode = d.target.id;
              let linkSet = origLinks.filter(l => l.source === sourceNode && l.target === targetNode);
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

              for (let id of sourceWordIDs) {sourceWords.push(lookupIDTable.get(id));}
              for (let id of targetWordIDs) {targetWords.push(lookupIDTable.get(id));}

              // sort words by line number, then by starting position in line
              sourceWords.sort((a,b) => d3.ascending(a.lineNum, b.lineNum) || d3.ascending(a.startPos, b.startPos));
              targetWords.sort((a,b) => d3.ascending(a.lineNum, b.lineNum) || d3.ascending(a.startPos, b.startPos));
              
              // get a list of the line numbers
              let sourceLineNums = new Set(sourceWords.map(word => word.lineNum));
              let targetLineNums = new Set(targetWords.map(word => word.lineNum));

              let textLinesSource = [];
              let textLinesTarget = [];

              // push author, then work, then section into text array
              let sourceAuthor = lookupIDTable.get(sourceNode).authorID;
              let targetAuthor = lookupIDTable.get(targetNode).authorID;
              
              textLinesSource.push(`${lookupIDTable.get(sourceAuthor)}, `);
              textLinesSource.push(`${lookupIDTable.get(sourceNode).work}`);
              textLinesSource.push(`, ${lookupIDTable.get(sourceNode).section}`);
              let firstLineLen = textLinesSource.length;  // set the number of elements that will be in the first line of text (i.e., author, work, section)
              textLinesTarget.push(`${lookupIDTable.get(targetAuthor)}, `);
              textLinesTarget.push(`${lookupIDTable.get(targetNode).work}`);
              textLinesTarget.push(`, ${lookupIDTable.get(targetNode).section}`);

              // push the line and words of that line into text array
              for (let line of sourceLineNums) {
                let proseCheck = lookupIDTable.get(sourceNode).meterID === proseID ? true : false; // check whether source segment is prose or poetry
                let linePrefix = 'line';
                if (proseCheck) { // if prose, prefix section symbol instead of 'line'
                  linePrefix = '\u00a7';
                }
                let text = `${linePrefix} ${line}: `;
                let words = sourceWords.filter(word => word.lineNum === line).map(word => word.word).join(', ');
                text += words;
                textLinesSource.push(text);
              }

              for (let line of targetLineNums) {
                let text = `line ${line}: `;
                let words = targetWords.filter(word => word.lineNum === line).map(word => word.word).join(', ');
                text += words;
                textLinesTarget.push(text);
              }

              // create tspan with appropriate styling for each element of the text array
              for (let arr of [textLinesSource, textLinesTarget]) {
                for (let i in arr) {
                  let indent = "5";
                  if (i > 0) {
                    indent = "15";
                  }
                  let textrow = tooltipLinksText
                    .append("tspan")
                      .attr("class", "tooltip-link-text-line");
                  if (i == 0) {
                    textrow
                      .attr("x", indent)
                      .attr("dy", "1em");
                  } else if (i == 1) { // using loose equality b/c i is apparently a text representation of the number
                    textrow
                      .attr("font-style", "italic");  // italicize title, which is the second element of the array
                  } else if (i >= firstLineLen) { // once we're past the elements of the first line, make an indented new line for each element
                    textrow
                      .attr("x", indent)
                      .attr("dy", "1em");
                  }
                  textrow.text(arr[i]); // set the text for the tspan
                }
              }
              
            }



                let linkText = d3.selectAll(".tooltip-link-text");
                linkText.each(function() {
                  let width = this.getBBox().width;
                  let height = this.getBBox().height;
                tooltipLinksBox.attr("width", width + 15).attr("height", height+15);
                })

            })
        .on("mouseleave", (e,d) => {
            d3.selectAll(".tooltip-link-text").remove();
            tooltipLinks
              .attr("transform", "rotate(-90,0,0) translate(50,-10)")
              .attr("opacity", "0")
              ;
        })




// Add text label to node

  if (Tl && sankeyType === "passage")

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
      .style('pointer-events', 'none')
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

else if (Tl && sankeyType === "word") {
  let wordList = [];
  node.each((d,i) => {
    let word = Tl[i];
    wordList.push(word);
  })

  //let nodeTextBg = node.append("rect").attr("class","node-word-text-bg");

  
  node
    .append("text")
    .attr("font-family", "sans-serif")
    .attr("font-size", 12)
    .attr("fill", "black")
    .attr("stroke","none")
    .attr("class", "node-word-text")
    .style('pointer-events', 'none')
    .each(function(d,i) {
      d3.select(this)
      .attr("id", `text-${d.id}`);

      d3.select(this)
      .append("tspan")
        .text(wordList[i]);
    })
    .each(function(d) {

      // label rotation help from ChatGPT
      const label = d3.select(this);
      
      const centerX = (d.x0 + d.x1) / 2;
      const centerY = (d.y0 + d.y1) / 2;

      if (rotateLabel) {
        label
          .attr("transform", `rotate(-90, ${centerX}, ${centerY})`)
          .attr("x", centerX)
          .attr("y", centerY)
          .attr("text-anchor", "middle")
          .attr("dominant-baseline", "middle")
          .attr("fill", "white")
          .attr("stroke", "black")
          .attr("stroke-width", ".5px")
          .attr("font-weight", "bold")
          ;

      // d3.selectAll(".node-word-text").each(function(d, i) {
      //   // this works to get the size of each word tspan, but still need to create the rectangle above and set its size here
      //   let bgWidth = this.firstChild.getBBox().height;
      //   let bgHeight = this.firstChild.getBBox().width;        
      // })

        
      } else {
        const x = d.x0 < width / 2 ? d.x1 + nodeLabelPadding : d.x0 - nodeLabelPadding;
        const y = centerY;

        label
          .attr("x", x)
          .attr("y", y)
          .attr("dy", "0.35em")
          .attr("text-anchor", d.x0 < width / 2 ? "start" : "end");
      }
    })
  ;
}


// add pop-up tooltips to nodes

const tooltipNodes = svg
  .append("g")
    .attr("class", "tooltip-node")
    .attr("transform", "rotate(-90,0,0) translate(50,-10)")
    .attr("opacity", "0")
    .style('pointer-events', 'none')
    ;

const tooltipNodesBox = tooltipNodes
    .append("rect")
      // .attr("height", "50") // get rid of this once I'm done
      // .attr("width", "140") // get rid of this once I'm done
      .attr("stroke","black")
      .attr("fill","white")
      .attr("filter","drop-shadow(0 3px 4px rgba(0,0,0,.5))");
  
nodeRect
  .on("mouseenter", function (e,d) {
    tooltipNodes
      .attr("opacity", "1");
    const tooltipNodesText = tooltipNodes
      .append("text")
        .attr("class", "tooltip-node-text")
        .attr("x","5")
        .attr("y",".5em")
        .attr("font-size","15")
        .attr("font-family","sans-serif")
        .attr("font-weight","normal")
        .attr("stroke","none")
        .attr("fill","black");

    let thisNode = origNodes.find(node => node.id === d.id);

    if (sankeyType === "passage") {

      let authorID = thisNode.author;
      let workID = thisNode.work;
      let workSection = lookupIDTable.get(thisNode.id).section;

        tooltipNodesText.append("tspan")
            .attr("dy","1em")
            .text(`${lookupIDTable.get(authorID)}, `)
        tooltipNodesText.append("tspan")
            // .attr("x","5")
            // .attr("dy","1em")
            .attr("font-style","italic")
            .text(lookupIDTable.get(workID));
        tooltipNodesText.append("tspan")
            .attr("x","5")
            .attr("dy","1em")
            .text(workSection);
    } else if (sankeyType === "word") {
      console.log(thisNode);
      let thisWord = lookupIDTable.get(thisNode.id);
      let author = lookupIDTable.get(thisWord.authorID);
      let work = lookupIDTable.get(thisWord.workID);
      let workSeg = lookupIDTable.get(thisWord.workSegID).section ? lookupIDTable.get(thisWord.workSegID).section : '';
      let proseCheck = lookupIDTable.get(thisWord.workSegID).meterID === proseID ? true : false;
      let linePrefix = proseCheck ? '\u00a7' : 'line';

      tooltipNodesText.append("tspan")
        .attr("dy", "1em")
        .text(`${author}, `);
      tooltipNodesText.append("tspan")
        // .attr("x", "5")
        // .attr("dy", "1em")
        .attr("font-style", "italic")
        .text(work);
      
      tooltipNodesText.append("tspan")
        .attr("x", "5")
        .attr("dy", "1em")
        .text(workSeg);
      
      tooltipNodesText.append("tspan")
        .text(` (${linePrefix} ${thisNode.line_num})`);
          
    }

  let nodeText = d3.selectAll(".tooltip-node-text");

  // set height and width of node tooltip

  let nodeBoxWidth;
  let nodeBoxHeight;
    nodeText.each(function() {
      nodeBoxWidth = this.getBBox().width;
      nodeBoxHeight = this.getBBox().height;
      tooltipNodesBox
        .attr("width", nodeBoxWidth + 15)
        .attr("height", nodeBoxHeight+15);
    })


  // based on height and width of tooltip box, place box relative to node

    let nodeRectHeight = d.x1 - d.x0;
    let nodeRectWidth = d.y1 - d.y0;

    let nodeLeft = d.y1;
    let nodeRight = d.y0;
    let nodeTop = d.x0;
    let nodeBottom = d.x1;

    if (d.x0 < width / 2) {
      tooltipNodes
        .attr("transform", `rotate(-90,0,0) translate(${(nodeLeft * -1) + nodeRectWidth/2}, ${nodeBottom + marginTop})`)
    } else {
      tooltipNodes
        .attr("transform", `rotate(-90,0,0) translate(${(nodeLeft * -1) + nodeRectWidth/2}, ${nodeTop - nodeBoxHeight - nodeRectHeight - marginTop})`)

    }

    })
  .on("mouseleave", (e,d) => {
    d3.selectAll(".tooltip-node-text").remove();
    tooltipNodes
      .attr("transform", "rotate(-90,0,0) translate(50,-10)")
      .attr("opacity", "0")
      ;
  });


// darken node and connected links when hovered over
nodeRect
  .on("mouseover", function(e, d) {
    d3.select(this).attr("opacity","1");
    svg.selectAll(`.link .source_${d.id}, .link .target_${d.id}`).attr("stroke-opacity", "1");
  })		
  .on("mouseout", function(event, d) {
    d3.select(this).attr("opacity",".6");
    svg.selectAll(`.link .source_${d.id}, .link .target_${d.id}`).attr("stroke-opacity", "0.5");
  });


// bring hovered node and its connected links to surface when hovered over
svg.selectAll(".node")
    .on("mouseover", function(event, d) {
        d3.select(this).raise();
        // if (sankeyType === "passage") {
          d3.selectAll(`.link .source_${d.id}, .link .target_${d.id}`).each(function() {d3.select(this.parentNode).raise()});
        // }
    })

// put a colored box around the word that was selected in the chart, which serves as the origin point of the word-level Sankey
if (sankeyType === "word") {
  node
    .attr("stroke", (d,i) => {
     if (origNodes[i].color) {return origNodes[i].color;}
    })
    .attr("stroke-width", (d,i) => {
     if (origNodes[i].color) {return 3;}
    })
  ;
}


// In order to not have tool-tips behind an adjacent SVG (thanks to ChatGPT!)
  const container = document.createElement("div");
  container.style.position = "relative";
  container.style.display = "inline-block";
  container.style.zIndex = 0;

  container.appendChild(svg_outer.node());

  svg_outer.node().addEventListener("mouseenter", () => {
    container.style.zIndex = 1000;
  });
  svg_outer.node().addEventListener("mouseleave", () => {
    container.style.zIndex = 0;
  });

// from the original function
  function intern(value) {
    return value !== null && typeof value === "object" ? value.valueOf() : value;
  }

// modified again to accommodate tool-tip overlaps
return Object.assign(container, {
    svg: svg_outer.node(),
    scales: { color },
    nodes,
    links
  });

  //  return Object.assign(svg_outer.node(), {scales: {color}, nodes: nodes, links: links});
}



export {SankeyChart};