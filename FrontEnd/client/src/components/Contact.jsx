import React from "react";

function Contact() {
  return (
    <div className="contact">
      <div class="container">
        <div class="row align-items-center my-5">
          <div style={{fontSize:'17px'}}>
            <h1 class="font-weight-dark">Contact</h1>
            <br></br>
            <p>
              This application is developed and maintained by team-tinkers.
              For any clarifications, please reach out to one of the team members.
            </p>
            <div class="list-group list-group-flush">
              <a href="mailto:anirudh.ganguly@sjsu.edu" style={{backgroundColor: 'rgb(39, 39, 39)', color:'white'}} class="list-group-item">Anirudh Ganguly</a>
              <a href="mailto:jocelyn.baduria@sjsu.edu" style={{backgroundColor: 'rgb(39, 39, 39)', color:'white'}} class="list-group-item">Jocelyn Baduria</a>
              <a href="mailto:sheema.murugeshbabu@sjsu.edu" style={{backgroundColor: 'rgb(39, 39, 39)', color:'white'}} class="list-group-item">Sheema Murugesh Babu</a>
            </div>

            <br />
            <br />
            <br />
            <br />
            <br />

          </div>
        </div>
      </div>
    </div>
  );
}

export default Contact;
