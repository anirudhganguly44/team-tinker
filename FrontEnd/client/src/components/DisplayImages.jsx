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

  render() {
    const imageList = this.state.data;
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
                <img src={file.src} width="200" alt="" />
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
                <img src={file.src} width="200" alt="" />
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
  }
}

//export default DisplayImages;
export default withRouter(DisplayImages);