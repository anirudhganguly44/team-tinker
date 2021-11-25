import React from "react";

function About() {
  return (
    <div className="about">
      <div class="container">
        <div class="row align-items-center my-5">
          <div >
            <h1 class="font-weight-dark">About</h1>
            <br></br>
            <div style={{fontSize:'17px'}}>
              <p style={{textAlign:'justify'}}>
                
              The “Automatic Data Cleaner” aims to remove incorrectly labeled data using deep learning image classification techniques. 
              These wrongly labeled data can cause overfitting of the model. This has been one of the underlying factors for poor performance in image classification.
              <br></br>
              <br></br>
              Overfitting happens when the model memorizes both the good and the noisy label during the training process. 
              "Automatic Data Cleaner" will focus on the root cause of the overfitting problem.
              <br></br>
              <br></br>
              Our solution has the capabilities of creating a new dataset using a search engine. 
              The created dataset can be uploaded for the automatic data cleaning process. 
              After the cleaning process, the "Automatic Data Cleaner" will provide feedback to the user on how many images were properly labeled. 
              Our solution achieved 75% ~ 85% cleaning accuracy which provides huge savings compared to human annotators.
              <br></br>
              <br></br>
              The 25% mislabeled can be renamed using our application. This saves a lot of time compared to manual relabeling. 
              The process can do the complete cycle of getting cleaned image datasets. The cleaned datasets can be downloaded and saved for any kind of Deep Learning training purposes.
              </p>
              <a href="/contact" style={{color:'white'}}> For further questions please contact us! </a>
            </div >
          </div>
        </div>
      </div>
    </div>
  );
}

export default About;