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

        {/* <Gallery images={imageList}/> */}

        {/* <table id="imagelist">
          <thead>
            <th>LABEL</th>
            <th colSpan="200">IMAGES</th>
          </thead>
          <tbody>
            <tr>
              <td>LABEL 1</td>
              <td>New Image 2<br/>New Name 2</td>
              <td>New Image 3<br/>New Name 3</td>
              <td>New Image 3<br/>New Name 3</td>
              <td>New Image 3<br/>New Name 3</td>
              <td>New Image 3<br/>New Name 3</td>
            </tr>
          </tbody>
        </table> */}

        {imageList.map((file) => (
          <div>
            <img src={file.src} />
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
