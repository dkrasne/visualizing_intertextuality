//import {FileAttachment} from "npm:@observablehq/stdlib";

// Attach restructured tables for querying
//const nodegoatTables = FileAttachment("../data/nodegoat_tables.json").json()

function createLookupIDTable(nodegoatTables) {
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

    return lookupIDTable;
}

export {createLookupIDTable};