 (function() {
  "use strict";

  var i, len, hash, key, value, raw,

    log = console.log,
    argv = process.argv,

    // require path and file system utilities to load the jshint.js file
    path = require('path'),
    fs = require('fs'),

    // the source file to be linted and options
    source = argv[2] || "",
    option = {};

  // the refactor functions work when global by dependance
  global.extractMethod = require(path.join(__dirname, "refactor-js.js")).extractMethod;

  // continue only if the source file is specified
  if (source !== "") {
    var tempFile = argv[3];
    // extra arguments with custom options could be passed, so check them now
    // and add them to the options object
    for (i = 4, len = argv.length; i < len; i++) {
      hash = argv[i].split(": ");
      key = hash[0];
      value = hash[1];

      // options are stored in key value pairs, such as option.es5 = true
      option[key] = value;
    }
  
    // read the source file and, when complete, refactor the code
    fs.readFile(source, "utf8", function(err, data) {
      if (err) {
        return;
      } 

      // refactor the code
      if (source.match(".js" + "$") == ".js") { 
        log(extractMethod(data, tempFile, option));
      }
    });
  }
}());
