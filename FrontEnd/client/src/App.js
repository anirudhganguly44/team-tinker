import React from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import { Navigation, Footer, Home, About, Contact, DisplayDataSets, DisplayImages } from "./components";


function App() {
  return (
    <div className="App">
      <Router>
        <Navigation />
        <Switch>
          <Route path="/" exact component={() => <Home />} />
          <Route path="/about" exact component={() => <About />} />
          <Route path="/contact" exact component={() => <Contact />} />
          <Route path="/displaydatasets" exact component={() => <DisplayDataSets />} />
          <Route path="/displayimages" exact component={() => <DisplayImages />} />
        </Switch>
        <Footer />
      </Router>
    </div>
  );
}

export default App;
