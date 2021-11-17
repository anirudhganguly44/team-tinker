import React from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import { Navigation, Home, About, Contact, DisplayDataSets, DisplayImages, Footer } from "./components";
import UploadImage from "./components/UploadImage";
import CreateDataSet from "./components/CreateDataSet";

function App() {
    return (
        <div className="App"> 
        <Router>
        <Navigation />
        <Switch>
            <Route path = "/" exact component = {() => < Home /> }/> 
            <Route path = "/about" exact component = {() => < About /> }/> 
            <Route path = "/contact" exact component = { () => < Contact />}/> 
            <Route path = "/displaydatasets" exact component = { () => < DisplayDataSets /> }/> 
            <Route path = "/displayimages" exact component = { () => < DisplayImages /> }/> 
            <Route path = "/uploadimage" exact component = { () => < UploadImage /> }/> 
            <Route path = "/create" exact component = { () => < CreateDataSet /> }/> 
            <Route path = "/footer" exact component = { () => < Footer /> }/> 
        </Switch> 
        </Router> 
        </div> 
    );
}

export default App;