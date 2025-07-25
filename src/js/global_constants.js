import * as d3 from "npm:d3";

//import {FileAttachment} from "npm:@observablehq/stdlib";

const proseID = "21025561";

function deepCopy(itemToCopy) {
    return JSON.parse(JSON.stringify(itemToCopy));
}

function createLookupIDTable(nodegoatTables) {
    const lookupIDTable = new Map();

    for (let i in nodegoatTables.word_instance_table) {
        let item = nodegoatTables.word_instance_table[i];
        let key = item.obj_id;
        let word = item.word;
        let line = `${item.line_num}${item.line_num_modifier ? item.line_num_modifier : ''}`;
        let workSegID = item.work_segment_id;
        let startPosLen = item.start_pos_id;
        let endPosLen = item.end_pos_id;
        let startPosID = nodegoatTables.meter_pos_len_table.find(pos => pos.obj_id === startPosLen).position_id;
        let endPosID = nodegoatTables.meter_pos_len_table.find(pos => pos.obj_id === endPosLen).position_id;
        let startPos = nodegoatTables.position_class_table.find(pos => pos.position_id === startPosID).position;
        let endPos = nodegoatTables.position_class_table.find(pos => pos.position_id === endPosID).position;
        let workID = nodegoatTables.work_seg_table.filter(workSeg => workSeg.obj_id === workSegID)[0].work_id;
        let authorID = nodegoatTables.work_table.filter(work => work.obj_id === workID)[0].author_id;
        let def = {'word': word, 'lineNum': line, 'workSegID': workSegID, 'workID': workID, 'authorID': authorID, 'startPos': startPos, 'endPos': endPos};
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
        let def = {'workTitle': item.title, 'authorID': item.author_id};
        lookupIDTable.set(key, def);
    }

    for (let i in nodegoatTables.work_seg_table) {
        let item = nodegoatTables.work_seg_table[i];
        let section = item.work_section || '';
        let subsec = item.work_subsection || '';
        let key = item.obj_id;
        let workID = String(item.work_id);
        let meterID = String(item.meter_id);
        let authorID = nodegoatTables.work_table.find(work => work.obj_id === workID).author_id;
        let work = lookupIDTable.get(workID).workTitle;
        let section_string;
        if (section && subsec) {
            section_string = `${section}, ${subsec}`;
        } else if (section) {
            section_string = `${section}`;
        } else {
            section_string = '';
        }
        let def = {'work': work, 'section': section_string, 'authorID': authorID, 'meterID': meterID, 'workID': workID};
        lookupIDTable.set(key, def);
    }

    for (let i in nodegoatTables.match_type_class_table) {
        let item = nodegoatTables.match_type_class_table[i];
        let key = item.match_type_id;
        let def = item.match_type;
        lookupIDTable.set(key, def);
    }

    // for (let i in nodegoatTables.sources_table) {
    //     let item = nodegoatTables.sources_table[i];
    //     let sourceType = item.source_type_id;
    //     let key = item.source_id;
    //     let author 
    // }
    for (let i in nodegoatTables.scholar_table) {
        let item = nodegoatTables.scholar_table[i];
        let key = item.obj_id;
        let def = `${item.surname}, ${item.forenames}`;
        lookupIDTable.set(key, def);
    }

    for (let i in nodegoatTables.publication_table) {
        let item = nodegoatTables.publication_table[i];
        let key = item.obj_id;
        let def = {authorIDs: item.author_ids}
        if (item.article_chapter_title) {def['articleChapterTitle'] = item.article_chapter_title}
        if (item.book_journal_title) {def['bookJournalTitle'] = item.book_journal_title}
        if (item.publication_date) {def['pubDate'] = item.publication_date} else {def['pubDate'] = 'forthcoming'}
        if (item.issue_number) {def['issueNumber'] = item.issue_number}
        lookupIDTable.set(key, def)
    }

    return lookupIDTable;
}


// this is the `glasbey_dark` set of colors from `colorcet`
const authorColors = ['#d60000', '#8c3bff', '#018700', '#00acc6', '#e6a500', '#ff7ed1', '#6b004f', '#573b00', '#005659', '#15e18c', '#0000dd', '#a17569', '#bcb6ff', '#bf03b8', '#645472', '#790000', '#0774d8', '#729a7c', '#ff7752', '#004b00', '#8e7b01', '#f2007b', '#8eba00', '#a57bb8', '#5901a3', '#e2afaf', '#a03a52', '#a1c8c8', '#9e4b00', '#546744', '#bac389', '#5e7b87', '#60383b', '#8287ff', '#380000', '#e252ff', '#2f5282', '#7ecaff', '#c4668e', '#008069', '#919eb6', '#cc7407', '#7e2a8e', '#00bda3', '#2db152', '#4d33ff', '#00e400', '#ff00cd', '#c85748', '#e49cff', '#1ca1ff', '#6e70aa', '#c89a69', '#77563b', '#03dae6', '#c1a3c3', '#ff6989', '#ba00fd', '#915280', '#9e0174', '#93a14f', '#364424', '#af6dff', '#596d00', '#ff3146', '#828056', '#006d2d', '#8956af', '#5949a3', '#773416', '#85c39a', '#5e1123', '#d48580', '#a32818', '#0087b1', '#ca0044', '#ffa056', '#eb4d00', '#6b9700', '#528549', '#755900', '#c8c33f', '#91d370', '#4b9793', '#4d230c', '#60345b', '#8300cf', '#8a0031', '#9e6e31', '#ac8399', '#c63189', '#015438', '#086b83', '#87a8eb', '#6466ef', '#c35dba', '#019e70', '#805059', '#826e8c', '#b3bfda', '#b89028', '#ff97b1', '#a793e1', '#698cbd', '#4b4f01', '#4801cc', '#60006e', '#446966', '#9c5642', '#7bacb5', '#cd83bc', '#0054c1', '#7b2f4f', '#fb7c00', '#34bf00', '#ff9c87', '#e1b669', '#526077', '#5b3a7c', '#eda5da', '#ef52a3', '#5d7e69', '#c3774f', '#d14867', '#6e00eb', '#1f3400', '#c14103', '#6dd4c1', '#46709e', '#a101c3', '#0a8289', '#afa501', '#a55b6b', '#fd77ff', '#8a85ae', '#c67ee8', '#9aaa85', '#876bd8', '#01baf6', '#af5dd1', '#59502a', '#b5005e', '#7cb569', '#4985ff', '#00c182', '#d195aa', '#a34ba8', '#e205e2', '#16a300', '#382d00', '#832f33', '#5d95aa', '#590f00', '#7b4600', '#6e6e31', '#335726', '#4d60b5', '#a19564', '#623f28', '#44d457', '#70aacf', '#2d6b4d', '#72af9e', '#fd1500', '#d8b391', '#79893b', '#7cc6d8', '#db9036', '#eb605d', '#eb5ed4', '#e47ba7', '#a56b97', '#009744', '#ba5e21', '#bcac52', '#87d82f', '#873472', '#aea8d1', '#e28c62', '#d1b1eb', '#36429e', '#3abdc1', '#669c4d', '#9e0399', '#4d4d79', '#7b4b85', '#c33431', '#8c6677', '#aa002d', '#7e0175', '#01824d', '#724967', '#727790', '#6e0099', '#a0ba52', '#e16e31', '#c46970', '#6d5b95', '#a33b74', '#316200', '#87004f', '#335769', '#ba8c7c', '#1859ff', '#909101', '#2b8ad4', '#1626ff', '#21d3ff', '#a390af', '#8a6d4f', '#5d213d', '#db03b3', '#6e56ca', '#642821', '#ac7700', '#a3bff6', '#b58346', '#9738db', '#b15093', '#7242a3', '#878ed1', '#8970b1', '#6baf36', '#5979c8', '#c69eff', '#56831a', '#00d6a7', '#824638', '#11421c', '#59aa75', '#905b01', '#f64470', '#ff9703', '#e14231', '#ba91cf', '#34574d', '#f7807c', '#903400', '#b3cd00', '#2d9ed3', '#798a9e', '#50807c', '#c136d6', '#eb0552', '#b8ac7e', '#487031', '#839564', '#d89c89', '#0064a3', '#4b9077', '#8e6097', '#ff5238', '#a7423b', '#006e70', '#97833d', '#dbafc8'];

export {createLookupIDTable, authorColors, proseID, deepCopy};