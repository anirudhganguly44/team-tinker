import React from "react";
import  DisplayDataSets from "./DisplayDataSets";




function Home() {
  return (
    <div className="home">
      <DisplayDataSets/>
        <div>
          {/* <a href="./viewloadimages">View the loaded images</a> */}
          <br></br>
          <br></br>
          {/* <a href="./displaydatasets">Click here to get datasets</a> */}
        </div>
      </div>
  );
}

export default Home;
