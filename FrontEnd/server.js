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
        // dict["thumbnail"] = path.join(folder, "/", file);
        // dict["thumbnailWidth"] = 320;
        // dict["thumbnailHeight"] = 320
        arrayOfFiles.push(dict);
      }
    });
    return arrayOfFiles;
  };

  // console.log('Current directory: ' + process.cwd());
  // Provide the folder location
  const arrayOfFiles = getAllFiles("./client/public/selfie-output");

  // var result = arrayOfFiles.reduce(function (r, a) {
  //   r[a.folderName] = r[a.folderName] || [];
  //   r[a.folderName].push(a);
  //   return r;
  // }, Object.create(null));
  // console.log(result);

  res.send({ express: arrayOfFiles });
});
