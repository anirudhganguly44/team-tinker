
// var fs = require('fs');
// const AdmZip = require('adm-zip');
// const zip = new AdmZip();

export const DownloadUtil = (directoryPath, directoryName) => {
    var dirPath = directoryPath;
    console.log(dirPath);

    // directoryName = directoryName+".zip";

    // fetch('http://localhost:5000/download?dir=' + dirPath, {
    //     method: 'GET',
    //     headers: {
    //         'Content-Type': 'application/octet-stream',
    //     },
    // })
    //     .then((response) => response.blob())
    //     .then((blob) => {
    //         // Create blob link to download
    //         const url = window.URL.createObjectURL(
    //             new Blob([blob]),
    //         );
    //         const link = document.createElement('a');
    //         link.href = url;
    //         link.setAttribute(
    //             'download',
    //             directoryName,
    //         );

    //         // Append to html link element page
    //         document.body.appendChild(link);

    //         // Start download
    //         link.click();

    //         // Clean up and remove the link
    //         link.parentNode.removeChild(link);
    //     });

}