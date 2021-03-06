const { response } = require("express");
const express = require("express");
const { spawn } = require("child_process");
const execSync = require('child_process').execSync;
const app = express();
const port = process.env.PORT || 3001;


// This displays message that the server running and listening to specified port
//app.listen(port, () => console.log(`Listening on port ${port}`));
//app.use(express.json());
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

    console.log("Contorl in get images API");
    const fs = require("fs");
    const path = require("path");

    var dirPathSelected = req.query.dir;
    var img_dir = dirPathSelected;
    files = fs.readdirSync(dirPathSelected);
    files.forEach(file => {
        if (fs.statSync(dirPathSelected + "/" + file).isFile() && file.includes("data.clean")) {
            img_dir = dirPathSelected + "/cleandataset"
        }
    })

    console.log("Path choosen for getImages: " + img_dir);

    const getAllFiles = function(dirPath, arrayOfFiles) {
        files = fs.readdirSync(dirPath);
        arrayOfFiles = arrayOfFiles || [];

        files.forEach(function(file) {
            dict = {};

            if (fs.statSync(dirPath + "/" + file).isDirectory()) {
                arrayOfFiles = getAllFiles(dirPath + "/" + file, arrayOfFiles);
            } else {

                if (file.includes("Store") || file.includes("unclean")) {
                    console.log("File include invalid file/folder: " + file + ". Hence skipping!");
                } else {
                    folder = dirPath.replace("./client/public", "");
                    folderName = dirPath.split(/(.*)[\/\\]/)[2];
                    dict["folderName"] = folderName;
                    dict["fileName"] = file;
                    dict["src"] = path.join(folder, "/", file);
                    // console.log("file:" + file);
                    fileNameSplit = file.split("_");
                    // console.log("fileNameSplit:" + fileNameSplit);
                    if (fileNameSplit.length != 2) {
                        dict["label"] = folderName;
                        dict["trueLabel"] = "";
                    } else {
                        fileLabel = fileNameSplit[0].split("-")[1];
                        fileTrueLabel = fileNameSplit[1].split("-")[1].split(".")[0];
                        dict["label"] = fileLabel;
                        dict["trueLabel"] = fileTrueLabel;
                    }
                    arrayOfFiles.push(dict);
                }
            }
        });
        return arrayOfFiles;
    };

    // console.log('Current directory: ' + process.cwd());
    // Provide the folder location
    const arrayOfFiles = getAllFiles(img_dir);

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
            ds_status = "unclean"
                // if (file.includes("Dataset-")) {
            subFile = fs.readdirSync(dirPath + "/" + file);
            subFile.forEach(sb => {
                if (fs.statSync(dirPath + "/" + file + "/" + sb).isFile()) {
                    if (sb.includes("data.clean")) {
                        ds_status = "clean";
                    } else if (sb.includes("inprogress")) {
                        ds_status = "inprogress";
                    }
                }
            })
            dict["path"] = dirPath + "/" + file;
            dict["name"] = file;
            dict["status"] = ds_status;
            dataSets.push(dict);
        }
    });
    res.send({ express: dataSets });
});


app.put("/train", (req, res) => {

    let folderToTrain = ".\\client\\public\\selfie-output\\" + req.body.Dataset; //Changed the path to relative to accomodate the file name change.

    //making the data.unclean file to data.inprogress to show on website that the training is in progress.
    const oldName = folderToTrain + "\\data.unclean";
    const newName = folderToTrain + "\\data.inprogress";
    const fs = require('fs');
    try {
        if (fs.existsSync(oldName)) {
            // console.log("File exists!");
            fs.rename(oldName, newName, (error) => {
                if (error) {
                    console.log("Error during rename: " + error);
                } else {
                    console.log("File renamed to in progress");
                }
            });
        } else {
            console.log("File does not exists.\n" + oldName);
        }
    } catch (err) {
        console.log(err);
    }

    const pythonScript = `C:\\sjsu\\project\\team-tinker\\prestopping\\main.py 0 custom DenseNet-25-12 PrestoppingPlus Symmetric 0.05 c:\\SELFIE ${folderToTrain}`;
    const environmentName = 'selfie';

    const command = [
            'echo \"%PATH%\"',
            'set PATH=\"%PATH%\";C:\\Users\\anirudh\\Anaconda3;C:\\Users\\anirudh\\Anaconda3\\Library\\mingw-w64\\bin;C:\\Users\\anirudh\\Anaconda3\\Library\\usr\\bin;C:\\Users\\anirudh\\Anaconda3\\Library\\bin;C:\\Users\\anirudh\\Anaconda3\\Scripts;C:\\Users\\anirudh\\Anaconda3\\bin;C:\\Users\\anirudh\\Anaconda3\\condabin;',
            `conda run -n ${environmentName} python ${pythonScript}`
        ]
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


    var download_dir = dirPath;
    files = fs.readdirSync(dirPath);
    files.forEach(file => {
        if (fs.statSync(dirPath + "/" + file).isFile() && file.includes("data.clean")) {
            console.log("Dataset clean. Hence changing the download folder to clean dataset!")
            download_dir = dirPath + "/cleandataset";
        }
    });

    console.log("Path choosen for download and zip: " + download_dir);

    zip.addLocalFolder(download_dir);

    folderName = dirPath.split(/(.*)[\/\\]/)[2];

    // Define zip file name
    const downloadName = folderName + '.zip';
    // console.log("Zipped folder name: " + downloadName);

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
 *  "filesrc": "./client/public/selfie-output/Dataset-Custom/cleandataset/0/0L-car_TL-car.png",
 *   "newtruelabel": "horse"
 * }
 * the file name will be renamed from old name to new name.
 * Yet to implement : exceptions
 */
app.post("/imagerename", (req, res) => {
    // console.log(req.body);

    console.log("Control in file rename API.");
    var oldFile = req.body.filesrc;
    var newtruelabel = req.body.newtruelabel;
    console.log(req.body);


    oldFileName = oldFile.split(/(.*)[\/\\]/)[2];
    console.log("Old file name: " + oldFileName);

    fileNameSplit = oldFileName.split("_");
    oldTrueLabel = fileNameSplit[1].split("-")[1].split(".")[0];
    fileExtn = fileNameSplit[1].split("-")[1].split(".")[1];

    newFileName = fileNameSplit[0] + "_" + "TL-" + newtruelabel + "." + fileExtn;
    console.log("The new file name: " + newFileName);

    // Import filesystem module
    const fs = require('fs');
    result = {};

    // oldName = ".\\client\\public\\" + oldFile;
    // newName = ".\\client\\public\\" + oldFile.split(/(.*)[\/\\]/)[1] + "\\" + newFileName;

    oldName = oldFile;
    newName = oldFile.split(/(.*)[\/\\]/)[1] + "/" + newFileName;

    console.log("Oldfile: " + oldName);
    console.log("Newfile: " + newName);

    try {
        if (fs.existsSync(oldName)) {
            // console.log("File exists!");
            fs.rename(oldName, newName, (error) => {
                if (error) {
                    console.log("Error during rename: " + error);
                    result["status"] = "failure";
                    result["error"] = error;
                    res.send({ express: result });
                } else {
                    if (fs.existsSync(newName)) {
                        console.log("File renamed!");
                        result["status"] = "success";
                        result["filesrc"] = req.body.fileSrc;
                        result["oldfilename"] = oldFileName;
                        result["newfilename"] = newFileName;

                        res.send({ express: result });
                    } else {
                        console.log("Error during rename. New file not found!");
                        result["status"] = "failure";
                        result["error"] = "Error during rename. New file not found!"
                        res.send({ express: result });

                    }
                }
            });
        } else {
            console.log("File not found!");
            result["status"] = "failure";
            result["error"] = "File not found!"
            res.send({ express: result });
        }
    } catch (err) {
        console.log(err);
        result["status"] = "failure";
        result["error"] = err;
        res.send({ express: result });
    }

});


/**
 * @author: sheemamb
 * Title: File delete API
 * The API requires a query string "file"
 * The query string should containt the filename including the path or simple called image source.
 * Response will be either success or failure with error message.
 * URL: http://localhost:3001/deletefile?file=.\client\public\selfie-output\Dataset-Custom\cleandataset\0\4L-car_TL-car.png
 * Response:
 * {
 *  "express": {
 *      "status": "success",
 *      "file": ".\\client\\public\\selfie-output\\Dataset-Custom\\cleandataset\\0\\4L-car_TL-car.png"
 *  }
 * }
 */
app.delete("/deletefile", (req, res) => {

    console.log("Control in file delete API.");
    var filePath = req.query.file;

    console.log("File that will be removed: " + filePath);

    const fs = require("fs")
    result = {};

    fs.unlink(filePath, function(err) {
        if (err) {
            console.log("Failed to delete the file.");
            console.log(err);
            result["status"] = "failure";
            result["file"] = filePath;
            result["error"] = err.message;
            res.send({ express: result });
            // throw err
        } else {
            console.log("Successfully deleted the file.")
            result["status"] = "success";
            result["file"] = filePath;
            res.send({ express: result });
        }
    })
});

app.delete("/deletedataset", (req, res) => {

    console.log("Control in file delete API.");
    var dir = "C:\\sjsu\\project\\team-tinker\\FrontEnd\\client\\public\\selfie-output\\" + req.query.dir;


    const fs = require("fs")
    fs.rmdir(dir, { recursive: true }, (err) => {
        if (err) {
            console.log("Failed to delete the file.");
            console.log(err);
            // throw err;
        }

        console.log(`${dir} is deleted!`);

    });
    res.status(204).send(req.body);


});


/**Unzip File into Folder*/
var unzip = require('unzipper');

/**Upload Images API */
var multer = require('multer')
var cors = require('cors');
app.use(cors())
    // var dataDir = 'client/public/selfie-output/data.unclean'
var dataDir = 'client/public/selfie-output/'
var storage = multer.diskStorage({
    destination: function(req, file, cb) {
        cb(null, dataDir);
    },
    filename: function(req, file, cb) {
        cb(null, Date.now() + '-' + file.originalname)
    }
});
var upload = multer({ storage: storage }).array('file')

app.get('/upload', function(req, res) {
    return res.send('Hello Server')
});

app.post('/upload', function(req, res) {
    //'/client/upload/selfie-output/uploadimages'
    console.log("Upload started.");
    upload(req, res, function(err) {

        if (err instanceof multer.MulterError) {
            console.log(err);
            return res.status(500).json(err)
                // A Multer error occurred when uploading.
        } else if (err) {
            console.log(err)
            return res.status(500).json(err)
                // An unknown error occurred when uploading.
        }

        console.log(`Uploaded ${req.files.length} files.`);

        var fs = require('fs')

        // unzip each files
        req.files.forEach(file => {
            console.log(`Unzipping: ${file.path}`);
            var targetDir;
            var n = 0;
            // Create a unique target dir for the zip file in the format
            // Dataset-date-sequence
            while (true) {
                targetDir = `${dataDir}/Dataset-${Date.now()}-${n}`;
                if (!fs.existsSync(targetDir)) {
                    fs.mkdirSync(targetDir);
                    break;
                }
                n = n + 1;
            }
            var zip = fs.createReadStream(file.path);
            zip.on('error', err => console.log("Error unzipping file: ", err));
            zip.on('close', () => {
                // delete the zip file
                console.log("unzip done.");
                fs.rmSync(file.path, { force: true });
                console.log("File is deleted.", file.path);
                console.log("File path.", targetDir);
                newDir = `${targetDir}//data.unclean`;
                fs.closeSync(fs.openSync(newDir, 'w', ));
                console.log("File is created.", newDir);
                // return res.status(200).send(req.files);
            });
            zip.pipe(unzip.Extract({ path: targetDir }));
        })
        res.end();
        // Everything went fine.
    })
});

app.put("/create", (req, res) => {

    var folderToCreate = "C:\\sjsu\\project\\team-tinker\\FrontEnd\\client\\public\\selfie-output\\" + req.body.Dataset;
    var label = req.body.Label;
    var count = req.body.Count;

    const pythonScript = `C:\\sjsu\\project\\team-tinker\\prestopping\\search_engine_api.py ${label} ${count} ${folderToCreate}`;
    const environmentName = 'tensorflow_gpuenv';

    const command = [
            'echo \"%PATH%\"',
            'set PATH=\"%PATH%\";C:\\Users\\anirudh\\Anaconda3;C:\\Users\\anirudh\\Anaconda3\\Library\\mingw-w64\\bin;C:\\Users\\anirudh\\Anaconda3\\Library\\usr\\bin;C:\\Users\\anirudh\\Anaconda3\\Library\\bin;C:\\Users\\anirudh\\Anaconda3\\Scripts;C:\\Users\\anirudh\\Anaconda3\\bin;C:\\Users\\anirudh\\Anaconda3\\condabin;',
            `conda run -n ${environmentName} python ${pythonScript}`
        ]
        .map(v => `(${v})`)
        .join(" && ");

    try {
        execSync(command, { shell: true });
    } catch (err) {}

    // pythonProcess.stdin.on('data', (data) => console.log(data.toString()));
    // pythonProcess.stderr.on('data', (data) => console.error(data.toString()));

    // pythonProcess.on('close', (code) => {
    //     console.log('Process Exited:', code);
    // });

    res.status(200).send(req.body);
});