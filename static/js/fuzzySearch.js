


// I can't figure out how to import this stupid function in main.js
//
// import {fuzzySearch} from "./fuzzySearch.js";
// 
// keeps giving me a syntax error: "Uncaught SyntaxError: Unexpected token {" in main.js:1


function fuzzySearch(query, target) {
    var matches = [];
    var i = 0;
    var j = 0;

    for (; i < query.length; i++) {

        if (typeof(query[i]) != "string" || query[i] == " ") { 
            continue; 
        }
        if (i + j > target.length - 1) { 
            return []; // Ran out of target to search
        }
        for (; j < target.length; j++) {
            if (query[i].toLowerCase() == target[j].toLowerCase()) {
                matches.push({"i": i, "j": j});
                break;
            }
        }
        
    }

    if (matches.length > 0 && matches[matches.length-1].i + 1 < i) {
        return []; // Not a match
    }
    return matches; // Match
}


	// Some tests:
    console.log(fuzzySearch("One Piece", "One.Piece"));
    console.log(fuzzySearch("OnePiece", "One.Piece"));
    console.log(fuzzySearch("Once", "One.Piece"));
    console.log(fuzzySearch("Oncek", "One.Piece"));