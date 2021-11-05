import React from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import { Navigation, Home, About, Contact, DisplayDataSets, DisplayImages } from "./components";
import UploadImages from "./components/UploadImages";

function App() {

    return ( <
        div className = "App" >
        <
        Router >
        <
        Navigation / >
        <
        Switch >
        <
        Route path = "/"
        exact component = {
            () => < Home / > }
        /> <
        Route path = "/about"
        exact component = {
            () => < About / > }
        /> <
        Route path = "/contact"
        exact component = {
            () => < Contact / > }
        /> <
        Route path = "/displaydatasets"
        exact component = {
            () => < DisplayDataSets / > }
        /> <
        Route path = "/displayimages"
        exact component = {
            () => < DisplayImages / > }
        /> <
        Route path = "/uploadimages"
        exact component = {
            () => < UploadImages / > }
        /> <
        /Switch> <
        /Router> <
        /div>
    );
}

export default App;