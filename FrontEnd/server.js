const express = require("express");
const app = express();
const port = process.env.PORT || 5000;

// This displays message that the server running and listening to specified port
app.listen(port, () => console.log(`Listening on port ${port}`));

// create a GET route
app.get("/getImages", (req, res) => {
  const fs = require("fs");
  const path = require("path");

  const getAllFiles = function (dirPath, arrayOfFiles) {
    files = fs.readdirSync(dirPath);

    arrayOfFiles = arrayOfFiles || [];

    files.forEach(function (file) {
      dict = {};
      if (fs.statSync(dirPath + "/" + file).isDirectory()) {
        arrayOfFiles = getAllFiles(dirPath + "/" + file, arrayOfFiles);
      } else {
        dict["folderName"] = dirPath.split(/(.*)[\/\\]/)[2];
        dict["fileName"] = file;
        dict["sourcePath"] = path.join(dirPath, "/", file);
        arrayOfFiles.push(dict);
      }
    });

    return arrayOfFiles;
  };

  // console.log('Current directory: ' + process.cwd());

  // Provide the folder location
  const result = getAllFiles(".\\selfie-output");
  
  // console.log(result);

  // console.log(Array.isArray(result))

  res.send({ express: result });
});
