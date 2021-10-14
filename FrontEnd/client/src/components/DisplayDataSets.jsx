import React from "react";
import { Link } from 'react-router-dom';

class GetDataSets extends React.Component {

  constructor(props) {
    super(props);
    this.state = { data: [] };
  }

  componentDidMount() {
    fetch("/getdatasets?dir=./client/public/selfie-output")
      .then((res) => res.json())
      .then((json) => this.setState({ data: json.express }));
  }

  OnClean(dataset)
  {
    console.log("Cleaning")
    const requestOptions = {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ Dataset: dataset })};

      fetch('/train', requestOptions)
  }

  render() {
    const datasetList = this.state.data;
    console.log(datasetList);
    console.log('Current directory: ' + process.cwd());
    return (

      <div class="wrapper">
        <table class="table" class="blueTable">
          <thead>
            <tr>
              <th>Dataset</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {
              datasetList.map((dataset) => (
                <tr>
                  <td>
                    <Link 
                    to= {{
                      pathname: '/displayimages?name=' + dataset.name
                    }}
                    >
                    {dataset.name}
                    </Link>
                  </td>
                  <td>{dataset.status}&emsp;
                  </td>
                  <td width="auto">
                      <input type="button" class="myButton" value="Download" />
                      <input type="button" class="myButton" onClick={() => this.OnClean(dataset.name)} value="Clean" />
                  </td>
                </tr>
              ))
            }
          </tbody>
        </table>
      </div>
    );
  }
}

export default GetDataSets;
