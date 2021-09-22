const express = require("express");
const app = express();
const port = process.env.PORT || 5000;

// This displays message that the server running and listening to specified port
app.listen(port, () => console.log(`Listening on port ${port}`));

// create a GET route
app.get("/getImages", (req, res) => {
  const fs = require("fs");
  const path = require("path");

  var dirPathSelected = req.query.dir;
  console.log("Path choosen: " + dirPathSelected);

  const getAllFiles = function (dirPath, arrayOfFiles) {
    files = fs.readdirSync(dirPath);
    arrayOfFiles = arrayOfFiles || [];
    files.forEach(function (file) {
      dict = {};
      if (fs.statSync(dirPath + "/" + file).isDirectory()) {
        arrayOfFiles = getAllFiles(dirPath + "/" + file, arrayOfFiles);
      } else {
        folder = dirPath.replace("./client/public", "");
        folderName = folder.split(/(.*)[\/\\]/)[2];
        dict["folderName"] = folderName;
        dict["fileName"] = file;
        dict["src"] = path.join(folder, "/", file);
        fileNameSplit = file.split("_");
        fileLabel = fileNameSplit[0].split("-")[1];
        fileTrueLabel = fileNameSplit[1].split("-")[1].split(".")[0];
        dict["label"] = fileLabel;
        dict["trueLabel"] = fileTrueLabel;
        arrayOfFiles.push(dict);
      }
    });
    return arrayOfFiles;
  };

  // console.log('Current directory: ' + process.cwd());
  // Provide the folder location
  const arrayOfFiles = getAllFiles(dirPathSelected);

  res.send({ express: arrayOfFiles });
});

app.get("/getdatasets", (req, res) => {
  const fs = require("fs");
  const path = require("path");

  var dirPath = req.query.dir;
  console.log("Path choosen: " + dirPath);

  // dirPath="./client/public/selfie-output";
  files = fs.readdirSync(dirPath);
  var dataSets = [];
  files.forEach(file => {
    if (fs.statSync(dirPath + "/" + file).isDirectory()) {
      // var file_name = file;
      if (file.includes("Dataset-")) {
        dset = dirPath + "/" + file
        dataSets.push(dset)
      }
    }
  });
  res.send({ express: dataSets });
});