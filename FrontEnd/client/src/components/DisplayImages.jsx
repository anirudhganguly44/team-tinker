import React from "react";
import { withRouter } from 'react-router-dom';
import queryString from 'query-string';
import Select from 'react-select';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

class DisplayImages extends React.Component {
  constructor() {
    super();
    this.state = {
      data: [],
      filter: false,
      filter_label: "default",
      TotalImages: 0,
      TotalLabels: 0,
      TotalCorrections: 0,
      loaded: 0
    };
  }

  componentDidMount() {

    let params = queryString.parse(this.props.location.search)
    fetch("/getimages?dir=./client/public/selfie-output/" + params.name)
      .then((res) => res.json())
      .then((json) => {
        var label_count = this.getTrueLabels(json.express).length
        this.setState({ data: json.express, TotalLabels: label_count, TotalImages: json.express.length, TotalCorrections: this.getCorrectedImageCount(json.express) });

      });
  }

  getCorrectedImageCount(datas) {
    var count = 0;
    datas.forEach(data => {
      if (data.label !== data.trueLabel)
        count = count + 1;
    });

    return count;
  }

  checkFilter = (evt) => {
    console.log("Hello");
    this.setState({ filter: evt.target.checked })
    this.forceUpdate();
  }

  checkSelectFilter = (evt) => {
    console.log("Hello");
    this.setState({ filter_label: evt.target.value })

    this.forceUpdate();
  }

  getTrueLabels(dataset) {
    console.log("In finding true labels!");
    var trueLabels = [];
    var results = [];
    dataset.forEach(imageSet => {
      const tlabel = imageSet.trueLabel;
      if (!(trueLabels.includes(tlabel))) {
        trueLabels.push(tlabel);
      }
    });
    console.log("True labels: " + trueLabels);

    trueLabels.forEach(label => {
      const dict = {};
      dict["value"] = label;
      dict["label"] = label;
      results.push(dict);
    });

    return results;

  }

  canShowImage(file) {
    if (this.state.filter === false) {
      if (this.state.filter_label === "default")
        return true;
      if (file.trueLabel === this.state.filter_label)
        return true;
    }
    else {
      if (file.label === file.trueLabel)
        return false;
      if (this.state.filter_label === "default")
        return true;
      if (file.trueLabel === this.state.filter_label)
        return true;
    }

    return false;

  }

  doDownload(imagePath) {
    console.log("Downloading dataset");

    console.log("original path folder: " + imagePath[0].src);
    var split1 = imagePath[0].src.split(/(.*)[\/\\]/)[1];
    // console.log("download path folder: "+split1);
    var split2 = split1.split(/(.*)[\/\\]/)[1];
    // console.log("Next slit path folder: "+split2);
    var dirPath = "./client/public/" + split2.split(/(.*)[\/\\]/)[1];
    console.log("downloadPath: " + dirPath);
    var dirName = dirPath.split(/(.*)[\/\\]/)[2];
    console.log("downloadName: " + dirName);

    var directoryName = dirName + ".zip";
    fetch('/download?dir=' + dirPath, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/octet-stream',
      },
    })
      .then((response) => response.blob())
      .then((blob) => {
        // Create blob link to download
        const url = window.URL.createObjectURL(
          new Blob([blob]),
        );
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute(
          'download',
          directoryName,
        );

        // Append to html link element page
        document.body.appendChild(link);

        // Start download
        link.click();

        // Clean up and remove the link
        link.parentNode.removeChild(link);
      });

  }

  renameSubmitNew  = (fileSrc, newLabel) => {
    console.log(fileSrc);
    console.log(newLabel.value);
    this.renameSubmit(fileSrc, newLabel)
  }

  renameSubmit(fileSrc, newLabel) {
    // document.getElementById("renamebtn").disabled = true;
    // this.state.nameSelected = false;
    console.log("In rename Submit group.");

    const headers = {
      'Content-Type': 'application/json',
      'Connection': 'keep-alive'
    }

    var requestBody = {
      "filesrc": "./client/public/" + fileSrc,
      "newtruelabel": newLabel
    };

    fetch("/imagerename",
      {
        headers: headers,
        method: "POST",
        body: JSON.stringify(requestBody)

      }
    )
      .then((res) => res.json())
      .then((json) => { // then print response status
        toast.success('rename success')
        window.location.reload(false);
      })
      .catch((err) => { // then print response status
        toast.error('rename fail. ' + err)
      })
  }

  deleteImage(fileSrc) {
    console.log("In image delete section.");
    fetch("/deletefile?file=./client/public/" + fileSrc,
      {
        method: "DELETE"
      }
    )
      .then(res => { // then print response status
        toast.success('Operation complete!')
        window.location.reload(false);
      })
      .catch(err => { // then print response status
        toast.error('Operation failed!')
      })

  }
  

  render() {
    const imageList = this.state.data;
    console.log(imageList);
    const trueLabelsList = this.getTrueLabels(imageList);
    // console.log("After get true labels: " + trueLabelsList);

    return (
      <div>
        <ToastContainer />
        <div className="stats">
          <label>Total Image Count: {this.state.TotalImages}</label><br />
          <label>Total Label Count: {this.state.TotalLabels}</label><br />
          <label>Total Corrected Image Count: {this.state.TotalCorrections}</label>
        </div>
        <div class="wrapper">
          <div class="box">
            <label>
              <input type="checkbox" defaultChecked={this.state.filter} onChange={this.checkFilter} id="filter" />
                Filter Only Corrected Images
            </label>
          </div>
          <div class="box"> Filter By Label</div>
          <div class="box">
            <select class="select_style" id="label_filter" onChange={this.checkSelectFilter}>
              <option value="default" selected>All</option>
              {trueLabelsList.map((truelabeloption) => (
                <option value={truelabeloption.value}>{truelabeloption.label}</option>
              ))}
            </select>
          </div>
        </div>
        <div class="button_group">
            <input type="button" class="myButton4" value="Download Dataset" id="DownloadDataset" onClick={(e) => this.doDownload(imageList)} />
        </div>
        <br/>
        <div className="home">
          <div class="parent">
            {imageList.map((file) => (
              this.canShowImage(file) &&
              <div class="child">
                <img src={file.src} alt="" />
                <br />
                Original Label = {file.label}
                <br />
                Corrected Label = {file.trueLabel}
                <br />
                <svg width="100%" height="1">
                  <rect width="100%" height="1" />
                </svg>
                <br />
                <div class="select">
                  {/* <Select options={trueLabelsList} 
                  placeholder={'UPDATE'}
                  onChange={(e) => this.renameSubmit(file.src, e.value)} /><br /> */}
                  <select class="select_style" onChange={(e) => this.renameSubmitNew(file.src, e.target.value)}>
                      <option value="none" selected disabled hidden>
                      Edit Label
                      </option>
                      {trueLabelsList.map((truelabeloption) => (
                      <option value={truelabeloption.value}>{truelabeloption.label}</option>
                  ))}
            </select>
                  <input type="button" class="myButton1" value="Delete" id={file.src} onClick={(e) => this.deleteImage(file.src)} />
                </div>
              </div>
            ))}

          </div>
          <p><br /><br /><br /></p>
          
        </div>
      </div>
    );


  }
}

//export default DisplayImages;
export default withRouter(DisplayImages);
