import React from "react";

function About() {
  return (
    <div className="about">
      <div class="container">
        <div class="row align-items-center my-5">
          <div >
            <h4 class="font-weight-dark">About</h4>
            <br></br>
            <div>
              <h5>
                
                The “Automatic Data Cleaner” aims to remove incorrectly labelled data using deep learning image classification techniques. 
                These wrongly labeled data can cause overfitting of the model. 
                This has been one of the underlying factors in image poor performance in classification. 
              <br></br>
              <br></br>
                Overfitting happens when the model memorizes both the good and the noisy label during the training process.
                Automatic Data cleaner will focus on the root cause of the overfitting problem. 
              <br></br>
              <br></br>
                Our solution has capabilities of creating new dataset using search engine. The created dataset can be uploaded for automatic data cleaning
                process. After the cleaning process the "Automatic Data Cleaner" will provide feedback to the user how may images were properly labeled. 
                Our solution achieved 75% ~ 85% cleaning accuracy which provides a huge savings compare for human annotator. 
              <br></br>
              <br></br>
                The 25% mislabeled can be renamed using our application. This is a huge reduction of time comparing to manual relabeling.
                The process can do the complete cycle of getting a cleaned image datasets. The cleaned datasets can be downloaded and saved for any kind of Deep Learning training purposes.
              </h5>
              <a href="/contact"> For further questions please contact us </a>
            </div >
          </div>
        </div>
      </div>
    </div>
  );
}

export default About;