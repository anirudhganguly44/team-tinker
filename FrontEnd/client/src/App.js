import React, { Component } from "react";
import "./App.css";

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
          <h1 className="App-title">Tinker Web App</h1>
        </header>
        <br />
        <br />
        {imageList.map((file) => (
          <div>
            <img src={file.sourcePath} />
            <br />
            Name = {file.fileName}
            <br />
            LABEL = {file.folderName}
            <br />
            <br />
          </div>
        ))}
      </div>
    );
  }
}

export default App;
