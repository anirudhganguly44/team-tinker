import React from "react";

class GetDataSets extends React.Component {

  constructor() {
    super();
    this.state = { data: [] };
  }

  componentDidMount() {
    fetch("/getdatasets?dir=./client/public/selfie-output")
      .then((res) => res.json())
      .then((json) => this.setState({ data: json.express }));
  }

  render() {
    const datasetList = this.state.data;
    console.log(datasetList);
    console.log('Current directory: ' + process.cwd());
    return (

      <div>
        <table class="table">
          <thead>
            <tr>
              <th>Dataset</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {
              datasetList.map((dataset) => (
                <tr>
                  <td>
                    <a href="/displayimages">
                      {dataset.name}
                    </a>
                  </td>
                  <td>{dataset.status}&emsp;
                    <a href="/displayimages">
                      <input type="button" value="Download" />
                    </a>
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
