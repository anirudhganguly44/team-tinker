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
    // const imageList = [];
    // this.state.data.map((imagePath) => imageList.push(imagePath.split("\\")));
    // console.log(imageList);

    return (
      <div className="App">
        <header className="App-header">
          <h1 className="App-title">Tinker Web App</h1>
        </header>
        <p>
          {this.state.data.map((filePath) => (
            <div>
            <img src={filePath} alt={filePath.split("\\")[(filePath.split("\\").length-2)]}/>
            </div>
          ))}
        </p>

        {/* <p>
          {this.state.data.map((filePath) => (

            <img src={filePath} />
          ))}
        </p> */}
      </div>
    );
  }
}

export default App;
