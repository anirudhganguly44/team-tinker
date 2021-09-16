import React, { Component } from "react";
import "./App.css";
import Gallery from 'react-grid-gallery';

class App extends Component {
  constructor() {
    super();
    this.state = { data: [] };
  }

  componentDidMount() {
    fetch("/getImages")
      .then((res) => res.json())
      .then((json) => this.setState({ data: json.express }));
  }

  render() {
    const imageList = this.state.data;
    // console.log(imageList);
    // console.log('Current directory: ' + process.cwd());

    return (
      <div className="App">
        <header className="App-header">
          <h1 className="App-title">Image Label Correction Web App</h1>
        </header>
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
      </div>
    );
  }
}

export default App;
