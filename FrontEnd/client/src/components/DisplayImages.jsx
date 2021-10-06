import React from "react";

class DisplayImages extends React.Component {
  constructor() {
    super();
    this.state = { data: [] };
  }

  componentDidMount() {
    fetch("/getimages?dir=./client/public/selfie-output/Dataset-09212021224733")
      .then((res) => res.json())
      .then((json) => this.setState({ data: json.express }));
  }

  render() {
    const imageList = this.state.data;
    // console.log(imageList);
    // console.log('Current directory: ' + process.cwd());
    return (
      <div className="home">
        <br />
        <br />

        <div class="parent">
          {imageList.map((file) => (
            <div class="child">
              <img src={file.src} />
              <br />
              Corrected Label = {file.folderName}
              <br />
              True Label = {file.trueLabel}
              <br />
              Label = {file.label}
              <br /><br />
            </div>
          ))}
        </div>
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
      </div>
    );
  }
}

export default DisplayImages;