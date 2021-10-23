import React from "react";
// import { DisplayDataSets } from "./DisplayDataSets";
// import UploadImages from "./UploadImages";
import UploadImage from "./UploadImage";



function Home() {
  return (
    <div className="home">
      <div class="container">
        <div class="row align-items-center my-5">
          <div class="col-lg-5">
            {/* <h1 class="font-weight-light">Upload Images</h1> */}
              <ul>
                {/* <UploadImages/> */}
                <UploadImage/>
                {/* <DisplayDataSets/> */}
              </ul>
            <div>
              <a href="./viewloadimages">View the loaded images</a>
              <br></br>
              <br></br>
              <a href="./displaydatasets">Click here to get datasets</a>
            </div >
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
