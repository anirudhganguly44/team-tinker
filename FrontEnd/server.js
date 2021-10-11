const { response } = require("express");
const express = require("express");
const app = express();
const port = process.env.PORT || 5000;


// This displays message that the server running and listening to specified port
app.listen(port, () => console.log('Listening on port: ' + port));

// This is required for using POST methods.
app.use(
  express.urlencoded({
    extended: true
  })
);

// To recognize the incoming Request Object as a JSON Object
app.use(express.json());

/** @author: sheemamb
 * Title: get Images API
 * This is an API to get all the images in a given dataset.
 * The API accepts a query string "dir"
 * The response is a Json.
 * The json is an array of dictionary values.
 * Each dictionary has below values:
 * Folder name, File name, source (path to the file),
 * Label, True Label.
 */
app.get("/getimages", (req, res) => {
  const fs = require("fs");
  const path = require("path");

  var dirPathSelected = req.query.dir;
  console.log("Path choosen for getImages: " + dirPathSelected);

  const getAllFiles = function (dirPath, arrayOfFiles) {
    files = fs.readdirSync(dirPath);
    arrayOfFiles = arrayOfFiles || [];
    files.forEach(function (file) {
      dict = {};
      if (fs.statSync(dirPath + "/" + file).isDirectory()) {
        arrayOfFiles = getAllFiles(dirPath + "/" + file, arrayOfFiles);
      } else {
        folder = dirPath.replace("./client/public", "");
        folderName = dirPath.split(/(.*)[\/\\]/)[2];
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

/** @author: sheemamb
 * Title: Get Datasets API
 * This is an API to get the list of datasets from given folder.
 * It accepts query string "dir"
 * The response is a json.
 * The json is an array of dictionary.
 * path, name, status
 * The status is defaulted to CLEAN
 */
app.get("/getdatasets", (req, res) => {
  const fs = require("fs");
  const path = require("path");

  var dirPath = req.query.dir;
  console.log("Path choosen for getDataSets: " + dirPath);

  // dirPath="./client/public/selfie-output";
  files = fs.readdirSync(dirPath);
  var dataSets = [];

  files.forEach(file => {
    if (fs.statSync(dirPath + "/" + file).isDirectory()) {
      // var file_name = file;
      dict = {};
      if (file.includes("Dataset-")) {
        dict["path"] = dirPath + "/" + file;
        dict["name"] = file;
        dict["status"] = "Clean";
        dataSets.push(dict);
      }
    }
  });
  res.send({ express: dataSets });
});

/** @author: sheemamb
 * Title: Download API
 * The API is a get method.
 * It accepts query string "dir"
 * The value should be path of the folder that needs to be zipped.
 * The zipped file will be downloaded to the location based on browser settings
 */
app.get("/download", (req, res) => {

  var fs = require('fs');
  const AdmZip = require('adm-zip');
  const zip = new AdmZip();

  var dirPath = req.query.dir;
  console.log("Path choosen for download and zip: " + dirPath);

  zip.addLocalFolder(dirPath);

  folderName = dirPath.split(/(.*)[\/\\]/)[2];

  // Define zip file name
  const downloadName = folderName + '.zip';
  console.log("Zipped folder name: " + downloadName);

  const data = zip.toBuffer();

  // save file zip in root directory if local downloading is not required
  // zip.writeZip(__dirname + "/" + downloadName);

  // code to download zip file
  res.set('Content-Type', 'application/octet-stream');
  res.set('Content-Disposition', 'attachment; filename=' + downloadName);
  res.set('Content-Length', data.length);
  res.send(data);

});


/** @author: sheemamb
 * Title: File rename API
 * The API requires a json request body
 * SAMPLE: 
 * {
 *  "folderLocation": "./client/public/selfie-output/Dataset-09212021224733/9",
 *   "oldName": "L-9_TL-9.jpg",
 *   "newName": "L-9_TL-9.png"
 * }
 * the file name will be renamed from old name to new name.
 * Yet to implement : exceptions
 */
app.post("/imagerename", (req, res) => {
  // console.log(req.body);

  var dirPath = req.body.folderLocation;
  var oldName = dirPath + "/" + req.body.oldName;
  var newName = dirPath + "/" + req.body.newName

  // Import filesystem module
  const fs = require('fs');
  result = {};

  fs.rename(oldName, newName, () => {
    console.log("File renamed!");
  });

  result["status"] = "success";
  result["folder"] = req.body.folderLocation;
  result["renameFrom"] = oldName;
  result["renameTo"] = newName;

  res.send({ express: result });
});
