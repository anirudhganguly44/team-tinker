import React from "react";
import { withRouter } from 'react-router-dom';
import queryString from 'query-string';

class DisplayImages extends React.Component {
  constructor() {
    super();
    this.state = {
      data: [],
      filter: false
    };
  }

  componentDidMount() {

    let params = queryString.parse(this.props.location.search)
    fetch("/getimages?dir=./client/public/selfie-output/" + params.name)
      .then((res) => res.json())
      .then((json) => this.setState({ data: json.express }));
  }

  checkFilter = (evt) => {
    console.log("Hello");
    this.setState({ filter: evt.target.checked })

    this.forceUpdate();
  }

  getTrueLabels(dataset) {

    console.log("In finding true labels!");
    var trueLabels = [];
    dataset.forEach(imageSet => {
      const tlabel = imageSet.trueLabel;
      if (!(trueLabels.includes(tlabel))) {
        trueLabels.push(tlabel);
      }
    });
    console.log("True labels: " + trueLabels);
    return trueLabels;

  }

  render() {
    const imageList = this.state.data;
    console.log(imageList);
    var trueLabelsList = this.getTrueLabels(imageList);
    console.log("After get true labels: " + trueLabelsList);
    if (this.state.filter === true) {
      return (
        <div>
          {<div>
            <label>
              <input type="checkbox" defaultChecked={this.state.filter} onChange={this.checkFilter} id="filter" />
              Filter Only Corrected Images
            </label>
          </div>}
          <div class="parent">
            {imageList.map((file) => (
              file.label !== file.trueLabel &&
              <div class="child">
                <img src={file.src} alt="" />
                <br />
                Original Label = {file.label}
                <br />
                Corrected Label = {file.trueLabel}
                <br />
              </div>
            ))}
          </div>
        </div>
      );
    }
    else {
      return (
        <div className="home">
          {<div>
            <label>
              <input type="checkbox" defaultChecked={this.state.filter} onChange={this.checkFilter} id="filter" />
              Filter Only Corrected Images
            </label>
          </div>}
          <div class="parent">
            {imageList.map((file) => (
              <div class="child">
                <img src={file.src} alt="" />
                <br />
                Original Label = {file.label}
                <br />
                Corrected Label = {file.trueLabel}
                <br /><br />
                <div>
                  <select name="truelabel" id="truelabel">
                    <option value="default" selected>select</option>
                    {trueLabelsList.map((truelabeloption) => (
                      <option value={truelabeloption}>{truelabeloption}</option>
                    ))}
                  </select>
                  <input type="button" value="Rename" id="renamebtn" />
                  <input type="button" value="Delete" id="deletebtn" />
                </div>
              </div>
            ))}

          </div>
        </div>
      );
    }
  }
}

//export default DisplayImages;
export default withRouter(DisplayImages);