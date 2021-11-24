import React from "react";
import { withRouter } from 'react-router-dom';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ReactLoading from "react-loading";

class CreateDataSet extends React.Component {
  constructor() {
    super();
    this.state = {
      data: [],
      datasetname: "",
      label: "",
      count: 0,
      label_count: 0,
      filter_label: "default",
      setDone: false,
    };
  }

  componentDidMount() {

    var dataset = document.getElementById('dataset_name').value;
    if (dataset != "") {
      fetch("/getimages?dir=./client/public/selfie-output/" + dataset)
        .then((res) => res.json())
        .then((json) => {
          this.setState({ data: json.express });

        });
    }
  }

  Generate = (evt) => {
    var dataset = document.getElementById('dataset_name').value;
    var label = document.getElementById('label').value;
    var count = document.getElementById('count').value;

    var requestBody = {
      "Dataset": dataset,
      "Label": label,
      "Count": count
    };

    axios.put("http://localhost:3001/create", requestBody).then(() => {
      fetch("/getimages?dir=./client/public/selfie-output/" + this.state.datasetname)
        .then((res) => res.json())
        .then((json) => {
          toast.success('rename success');
          var label_count = this.getTrueLabels(json.express).length
          this.setState({ data: json.express });
        })

      this.forceUpdate()
    })
  }

  Save = (evt) => {
    window.open("/displaydatasets")
  }

  Cancel = (evt) => {

    var requestBody = {
      "Dataset": this.state.datasetname,
    };

    axios.delete("http://localhost:3001/deletedataset?dir=" + this.state.datasetname).then(() => {
      window.open("/displaydatasets")
    })
  }

  canShowImage(file) {

    if (this.state.filter_label === "default")
      return true;
    if (file.label === this.state.filter_label)
      return true;


    return false;

  }

  getTrueLabels(dataset) {
    console.log("In finding true labels!");
    var trueLabels = [];
    var results = [];
    dataset.forEach(imageSet => {
      const tlabel = imageSet.label;
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

  checkSelectFilter = (evt) => {
    console.log("Hello");
    this.setState({ filter_label: evt.target.value })

    this.forceUpdate();
  }

  handleDatasetChange = (e) => {
    this.setState({ datasetname: e.target.value });
  };

  handleLabelChange = (e) => {
    this.setState({ label: e.target.value });
  };

  handleCountChange = (e) => {
    this.setState({ count: e.target.value });
  };

  render() {
    const imageList = this.state.data;
    console.log(imageList);
    const trueLabelsList = this.getTrueLabels(imageList);

    return (
      <div>
        <div class="wrapper-create">
          <ToastContainer />
          <label>Dataset Name</label> <br />
          <input type="text" size="100" value={this.state.datasetname} onChange={this.handleDatasetChange} id="dataset_name" ></input> <br /> <br />
          <label>Label</label> <br />
          <input type="text" size="100" value={this.state.label} onChange={this.handleLabelChange} id="label"></input> <br /> <br />
          <label>Number of Images</label> <br />
          <input type="text" size="100" value={this.state.count} onChange={this.handleCountChange} id="count"></input> <br /> <br />
          <input type="button" class="myButton_create" value="Generate" onClick={this.Generate} />
          <input type="button" class="myButton_create" value="Save" onClick={this.Save} />
          <input type="button" class="myButton_create" value="Cancel" onClick={this.Cancel} />
          <br />

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

        <div class="wrapper">
          <div className="home">
            <div class="parent">
              {imageList.map((file) => (
                this.canShowImage(file) &&
                <div class="child">
                  <img src={file.src} alt="" />
                  <br />
                  <svg width="100%" height="1">
                    <rect width="100%" height="1" />
                  </svg>
                  <br />
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    );


  }
}


export default withRouter(CreateDataSet);
