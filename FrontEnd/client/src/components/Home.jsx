import React from "react";

// class Home extends React.Component {
//   constructor() {
//     super();
//     this.state = { data: [] };
//   }

//   componentDidMount() {
//     fetch("/getimages?dir=./client/public/selfie-output/Dataset-09212021224733")
//       .then((res) => res.json())
//       .then((json) => this.setState({ data: json.express }));
//   }

//   render() {
//     const imageList = this.state.data;
//     // console.log(imageList);
//     // console.log('Current directory: ' + process.cwd());
//     return (
//       <div className="home">
//         <br />
//         <br />

//         <div class="parent">
//           {imageList.map((file) => (
//             <div class="child">
//               <img src={file.src} />
//               <br />
//               Corrected Label = {file.folderName}
//               <br />
//               True Label = {file.trueLabel}
//               <br />
//               Label = {file.label}
//               <br /><br />
//             </div>
//           ))}
//         </div>
//         <br />
//         <br />
//         <br />
//         <br />
//         <br />
//         <br />
//         <br />
//         <br />
//         <br />
//         <br />
//       </div>
//     );
//   }
// }


//************ Get Datasets Code ******* */
// class Home extends React.Component {

//     constructor() {
//       super();
//       this.state = { data: [] };
//     }
  
//     componentDidMount() {
//       fetch("/getdatasets?dir=./client/public/selfie-output")
//         .then((res) => res.json())
//         .then((json) => this.setState({ data: json.express }));
//     }
  
//     render() {
//       const datasetList = this.state.data;
//       console.log(datasetList);
//       console.log('Current directory: ' + process.cwd());
//       return (
//         <div>
//           <br />
//           <br />
//           {
//             datasetList.map((dataset) => (
//               <div>
//                 <a href ={dataset}>
//                 {dataset.split(/(.*)[\/\\]/)[2]}
//                 </a>
//               </div>
//             ))
//           }
//         </div>
//       );
//     }
//   }

//*******************/

function Home() {
  return (
    <div className="home">
      <div class="container">
        <div class="row align-items-center my-5">
          <div class="col-lg-5">
            <h1 class="font-weight-light">Home</h1>
            <div>
              <a href="./displaydatasets">Click here to get datasets</a>
            </div >
          </div>
        </div>
      </div>
    </div>
  );
}
//*************** */

export default Home;
