const express = require("express");
const {spawn} = require("child_process");
const app = express();
const port = process.env.PORT || 5000;

// This displays message that the server running and listening to specified port
app.listen(port, () => console.log(`Listening on port ${port}`));
app.use(express.json());

// create a GET route
app.get("/getimages", (req, res) => {
  const fs = require("fs");
  const path = require("path");

  var dirPathSelected = req.query.dir;
  var img_dir = dirPathSelected
  files = fs.readdirSync(dirPathSelected);
  files.forEach(file => {
    if (fs.statSync(dirPathSelected + "/" + file).isFile() && file.includes("data.clean"))
    {
      img_dir = dirPathSelected + "/cleandataset"
    }
  })

  console.log("Path choosen for getImages: " + img_dir);

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
        if(fileNameSplit.length == 1)
        {
          dict["label"] = folderName;
          dict["trueLabel"] = "";
        }
        else
        {
          fileLabel = fileNameSplit[0].split("-")[1];
          fileTrueLabel = fileNameSplit[1].split("-")[1].split(".")[0];
          dict["label"] = fileLabel;
          dict["trueLabel"] = fileTrueLabel;
        }
        arrayOfFiles.push(dict);
      }
    });
    return arrayOfFiles;
  };

  // console.log('Current directory: ' + process.cwd());
  // Provide the folder location
  const arrayOfFiles = getAllFiles(img_dir);

  res.send({ express: arrayOfFiles });
});

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
      ds_status = "unclean"
      if (file.includes("Dataset-")) {
        subFile = fs.readdirSync(dirPath + "/" + file);
        subFile.forEach(sb => {
          if (fs.statSync(dirPath + "/" + file + "/" + sb).isFile()){
          if(sb.includes("data.clean"))
          {
            ds_status = "clean";
          }
        }
        })
        dict["path"] = dirPath + "/" + file;
        dict["name"] = file;
        dict["status"] = ds_status;
        dataSets.push(dict);
      }
    }
  });
  res.send({ express: dataSets });
});

app.put("/train", (req, res) => {
  
  let folderToTrain = "C:\\sjsu\\project\\team-tinker\\FrontEnd\\client\\public\\selfie-output\\" + req.body.Dataset;

  const pythonScript = `C:\\sjsu\\project\\prestopping\\main.py 0 custom DenseNet-25-12 PrestoppingPlus Symmetric 0.2 c:\\SELFIE ${folderToTrain}`;
  const environmentName = 'selfie';

  const command = [
    'echo \"%PATH%\"',
    'set PATH=\"%PATH%\";C:\\Users\\anirudh\\Anaconda3;C:\\Users\\anirudh\\Anaconda3\\Library\\mingw-w64\\bin;C:\\Users\\anirudh\\Anaconda3\\Library\\usr\\bin;C:\\Users\\anirudh\\Anaconda3\\Library\\bin;C:\\Users\\anirudh\\Anaconda3\\Scripts;C:\\Users\\anirudh\\Anaconda3\\bin;C:\\Users\\anirudh\\Anaconda3\\condabin;',
    `conda run -n ${environmentName} python ${pythonScript}`]
    .map(v => `(${v})`)
  .join(" && ");

  const pythonProcess = spawn(command, { shell: true });

  pythonProcess.stdin.on('data', (data) => console.log(data.toString()));
  pythonProcess.stderr.on('data', (data) => console.error(data.toString()));

  pythonProcess.on('close', (code) => {
  console.log('Process Exited:', code);
  });

  res.status(200).send(req.body);
});