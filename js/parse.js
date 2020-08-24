var UglifyJS = require("uglify-js");
var beautify = require('js-beautify').js_beautify;
var fs = require("fs");
var path = require("path");
var util = require("util");
 
var normalizedCode = null; 
var extractedFunctionName = "method_name";
var parmsName = "self";

var isJavascriptKeyword;
(function() {
	isJavascriptKeyword = function testJavascriptKeyword (argument) {
		var type = "undefined";
		try {
			if (argument === type){
				return true;
			} else {
				eval("type = typeof " + argument + ";");
			}
		} catch (e) {
		} finally {
			//console.log(type);
		}
		 
		return type !== "undefined";
	};
})();

function extractMethod(code, tempFile, options, debug){
	normalizedCode = beautify(code); 
	var orignialCode = code; 
	var parms = [] ; 
	var parmsJSON = [];
	var toplevel = UglifyJS.parse(normalizedCode, { bare_returns : true });
	toplevel.figure_out_scope();

	var stream = new UglifyJS.OutputStream({
		comments : true,
		preserve_line : false,
		
	});
    
	var walker = new UglifyJS.TreeWalker(function(node){
		var varName = node.end.value;
		var isVar = (node.end.type === "name"); 

		if (node.thedef && isVar && !isJavascriptKeyword(varName)){
			if (true){
				var varUndeclared  = node.thedef.undeclared;  
				var varNested = (node.scope.nesting !== 0);
				var nextChar = normalizedCode.substring(node.start.endpos, node.start.endpos+1);
				var isFunctionCall = (nextChar === "(");  

				if ( !varNested && varUndeclared ){  
					//if (varName==="String") console.log( node); 
					if (!isFunctionCall && parms.indexOf(varName) === -1 ) {
						parms.push(varName);
						parmsJSON.push();
						node.thedef.mangled_name = parmsName + "." + varName;
					}   
				} 
			}
		}
	});
	toplevel.walk(walker); 
	toplevel.print(stream);
	 
	exports.parms = parms; // keep parms for mocha testing

	parms = JSON.stringify(parmsJSON).replace(/"/g,"").replace("[", "(").replace("]", ")");
	var cal = extractedFunctionName+parms;
	var fun = "def "+extractedFunctionName+"("+parmsName+"):"+"\n"+stream;
	exports.fu = fun; // keep extracted function string for mocha testing
	var result = beautify(fun+"\n\n"+cal, options);
	if (debug) {
		console.log("-");
		console.warn("// Original selected Source Code:");
		console.log(beautify(orignialCode));
		console.log("-");
		console.log("// Extracted Methode from original selected Source Code:");
		console.log(beautify(fun));
		console.log("-");
		console.log("// Extracted Methode call from original selected Source Code:");
		console.log(beautify(cal));
	}


	return result; 
}

var i =0;




if (typeof exports !== "undefined"){
	exports.extractMethod = extractMethod; 
}