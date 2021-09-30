import React from "react";

//** ******************/
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
        <br />
        <br />
        {
          datasetList.map((dataset) => (
            <div>
              <a href="./displayimages">{dataset}</a>
            </div>
          ))
        }
      </div>
    );
  }
}
//**************** */


// function GetDataSets() {
//     return (
//       <div className="getsets">
//               <p>
//                 This is Get Datasets page!!!
//               </p>
//             </div>
//     );
//   }

export default GetDataSets;
