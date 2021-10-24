const { response } = require("express");
const express = require("express");
const { spawn } = require("child_process");
const app = express();
const port = process.env.PORT || 5000;


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
    const fs = require("fs");
    const path = require("path");

    var dirPathSelected = req.query.dir;
    var img_dir = dirPathSelected
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
                folder = dirPath.replace("./client/public", "");
                folderName = dirPath.split(/(.*)[\/\\]/)[2];
                dict["folderName"] = folderName;
                dict["fileName"] = file;
                dict["src"] = path.join(folder, "/", file);
                fileNameSplit = file.split("_");
                if (fileNameSplit.length == 1) {
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
            if (file.includes("Dataset-")) {
                subFile = fs.readdirSync(dirPath + "/" + file);
                subFile.forEach(sb => {
                    if (fs.statSync(dirPath + "/" + file + "/" + sb).isFile()) {
                        if (sb.includes("data.clean")) {
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

/**Upload ZIP Images API */
// app.get("/uploadimages", (req, res) => {

//   const fs = require("fs");
//   const path = require("path");

//   const ZipLoader = require('ziploader-zip');
//   const loader = new ZipLoader('./foldername.zip' );
//   loader.load();

//   // var loader = new ZipLoader( './496_RPG_icons.zip' );
// // on progress
//   loader.on( 'progress', function ( e ) {
//     console.log(
//       'loading',
//       e.loaded / e.total * 100 + '%',
//       'time:' + e.elapsedTime + 'ms'
//     );
//   } );
//   // on load
//   loader.on( 'load', function ( e ) {
//     Object.keys( loader.files ).forEach( function ( filename ) {
//       var img = new Image();
//       var url = loader.extractAsBlobUrl( filename, 'image/png' );
//       img.onload = function () {
//         document.body.appendChild( img );
//         loader.clear( filename );
//       }
//       img.src = url;
//     } );
//   } );
//   });
//   // on button click
//   document.getElementById( 'button' ).addEventListener( 'click', function ( e ) {

//     loader.load();
//     e.target.disabled = true;
//   } );

/**Upload Images API */
var multer = require('multer')
var cors = require('cors');
app.use(cors())
var storage = multer.diskStorage({
    destination: function(req, file, cb) {
        cb(null, 'client/public/selfie-output/data.unclean');
    },
    filename: function(req, file, cb) {
        cb(null, /* Date.now() + '-' + */ file.originalname)
    }
});
var upload = multer({ storage: storage }).array('file')

app.get('/upload', function(req, res) {
    return res.send('Hello Server')
});

app.post('/upload', function(req, res) {
    //'/client/upload/selfie-output/uploadimages'
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

        return res.status(200).send(req.file)
            // Everything went fine.
    })
});