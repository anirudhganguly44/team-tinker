(this.webpackJsonpclient=this.webpackJsonpclient||[]).push([[0],{44:function(e,t,n){},45:function(e,t,n){},88:function(e,t,n){"use strict";n.r(t);var c=n(0),a=n.n(c),l=n(13),s=n.n(l),r=(n(44),n(12)),i=n(4),o=(n(45),n(1));var d=Object(i.f)((function(e){return Object(o.jsx)("div",{className:"navigation",children:Object(o.jsx)("nav",{class:"navbar navbar-expand navbar-dark bg-dark",children:Object(o.jsxs)("div",{class:"container",children:[Object(o.jsx)(r.b,{class:"navbar-brand",to:"/",children:"Automatic Label Correction"}),Object(o.jsx)("div",{children:Object(o.jsxs)("ul",{class:"navbar-nav ml-auto",children:[Object(o.jsx)("li",{class:"nav-item  ".concat("/"===e.location.pathname?"active":""),children:Object(o.jsxs)(r.b,{class:"nav-link",to:"/",children:["Home",Object(o.jsx)("span",{class:"sr-only",children:"(current)"})]})}),Object(o.jsx)("li",{class:"nav-item  ".concat("/about"===e.location.pathname?"active":""),children:Object(o.jsx)(r.b,{class:"nav-link",to:"/about",children:"About"})}),Object(o.jsx)("li",{class:"nav-item  ".concat("/contact"===e.location.pathname?"active":""),children:Object(o.jsx)(r.b,{class:"nav-link",to:"/contact",children:"Contact"})})]})})]})})})}));var b=n(7),j=n(8),u=n(9),h=n(14),O=function(e){Object(u.a)(n,e);var t=Object(h.a)(n);function n(e){var c;return Object(b.a)(this,n),(c=t.call(this,e)).state={data:[]},c}return Object(j.a)(n,[{key:"componentDidMount",value:function(){var e=this;fetch("/getdatasets?dir=./client/public/selfie-output").then((function(e){return e.json()})).then((function(t){return e.setState({data:t.express})}))}},{key:"OnClean",value:function(e){console.log("Cleaning");var t={method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({Dataset:e})};fetch("/train",t)}},{key:"OnDownload",value:function(e,t){console.log("Downloading dataset");var n=t+".zip";fetch("/download?dir="+e,{method:"GET",headers:{"Content-Type":"application/octet-stream"}}).then((function(e){return e.blob()})).then((function(e){var t=window.URL.createObjectURL(new Blob([e])),c=document.createElement("a");c.href=t,c.setAttribute("download",n),document.body.appendChild(c),c.click(),c.parentNode.removeChild(c)}))}},{key:"render",value:function(){var e=this,t=this.state.data;return Object(o.jsxs)("div",{className:"wrapper",children:[Object(o.jsxs)("table",{className:"table blueTable",children:[Object(o.jsx)("thead",{children:Object(o.jsxs)("tr",{children:[Object(o.jsx)("th",{children:"Dataset"}),Object(o.jsx)("th",{children:"Status"}),Object(o.jsx)("th",{children:"Actions"})]})}),Object(o.jsx)("tbody",{children:t.map((function(t){return Object(o.jsxs)("tr",{children:[Object(o.jsx)("td",{children:Object(o.jsx)("div",{style:{"text-transform":"uppercase"},children:Object(o.jsxs)("a",{className:"hyperlink",href:"/displayimages?name="+t.name,children:[" ",Object(o.jsx)("div",{children:t.name})," "]})})}),Object(o.jsx)("td",{style:{"text-transform":"uppercase"},children:t.status}),Object(o.jsxs)("td",{width:"auto",children:["clean"===t.status&&Object(o.jsx)("input",{type:"button",class:"myButton1",onClick:function(){return e.OnDownload(t.path,t.name)},value:"Download"}),"clean"===t.status&&Object(o.jsx)("input",{type:"button",class:"myButton1",onClick:function(){return e.OnClean(t.name)},value:"Clean",disabled:!0}),"unclean"===t.status&&Object(o.jsx)("input",{type:"button",class:"myButton1",onClick:function(){return e.OnDownload(t.path,t.name)},value:"Download",disabled:!0}),"unclean"===t.status&&Object(o.jsx)("input",{type:"button",class:"myButton1",onClick:function(){return e.OnClean(t.name)},value:"Clean"})]})]})}))})]}),Object(o.jsx)("a",{type:"button",class:"myButton2",href:"./uploadimage",children:"Upload"}),Object(o.jsx)("br",{}),Object(o.jsx)("a",{type:"button",class:"myButton2",href:"./createimage",children:"Create"})]})}}]),n}(a.a.Component);var f=function(){return Object(o.jsx)("div",{className:"home",children:Object(o.jsx)("div",{class:"container",children:Object(o.jsx)("div",{class:"row align-items-center my-5",children:Object(o.jsxs)("div",{class:"col-lg-5",children:[Object(o.jsx)("ul",{children:Object(o.jsx)(O,{})}),Object(o.jsxs)("div",{children:[Object(o.jsx)("br",{}),Object(o.jsx)("br",{})]})]})})})})};var p=function(){return Object(o.jsx)("div",{className:"about",children:Object(o.jsx)("div",{class:"container",children:Object(o.jsxs)("div",{class:"row align-items-center my-5",children:[Object(o.jsx)("div",{class:"col-lg-7",children:Object(o.jsx)("img",{class:"img-fluid rounded mb-4 mb-lg-0",src:"http://placehold.it/900x400",alt:""})}),Object(o.jsxs)("div",{class:"col-lg-5",children:[Object(o.jsx)("h1",{class:"font-weight-light",children:"About"}),Object(o.jsx)("div",{children:Object(o.jsx)("a",{href:"/contact",children:"Click here to go to Contact"})})]})]})})})};var x=function(){return Object(o.jsx)("div",{className:"contact",children:Object(o.jsx)("div",{class:"container",children:Object(o.jsxs)("div",{class:"row align-items-center my-5",children:[Object(o.jsx)("div",{class:"col-lg-7",children:Object(o.jsx)("img",{class:"img-fluid rounded mb-4 mb-lg-0",src:"http://placehold.it/900x400",alt:""})}),Object(o.jsxs)("div",{class:"col-lg-5",children:[Object(o.jsx)("h1",{class:"font-weight-light",children:"Contact"}),Object(o.jsxs)("p",{children:["This is Contact us page.",Object(o.jsx)("br",{}),Object(o.jsx)("br",{}),Object(o.jsx)("br",{}),Object(o.jsx)("br",{}),Object(o.jsx)("br",{})]})]})]})})})},m=n(37),v=n.n(m),g=n(38),y=n(16),C=n.n(y),k=n(11),w=(n(33),function(e){Object(u.a)(n,e);var t=Object(h.a)(n);function n(){var e;return Object(b.a)(this,n),(e=t.call(this)).checkFilter=function(t){console.log("Hello"),e.setState({filter:t.target.checked}),e.forceUpdate()},e.checkSelectFilter=function(t){console.log("Hello"),e.setState({filter_label:t.target.value}),e.forceUpdate()},e.state={data:[],filter:!1,filter_label:"default",TotalImages:0,TotalLabels:0,TotalCorrections:0,loaded:0},e}return Object(j.a)(n,[{key:"componentDidMount",value:function(){var e=this,t=v.a.parse(this.props.location.search);fetch("/getimages?dir=./client/public/selfie-output/"+t.name).then((function(e){return e.json()})).then((function(t){var n=e.getTrueLabels(t.express).length;e.setState({data:t.express,TotalLabels:n,TotalImages:t.express.length,TotalCorrections:e.getCorrectedImageCount(t.express)})}))}},{key:"getCorrectedImageCount",value:function(e){var t=0;return e.forEach((function(e){e.label!==e.trueLabel&&(t+=1)})),t}},{key:"getTrueLabels",value:function(e){console.log("In finding true labels!");var t=[],n=[];return e.forEach((function(e){var n=e.trueLabel;t.includes(n)||t.push(n)})),console.log("True labels: "+t),t.forEach((function(e){var t={};t.value=e,t.label=e,n.push(t)})),n}},{key:"canShowImage",value:function(e){if(!1===this.state.filter){if("default"===this.state.filter_label)return!0;if(e.trueLabel===this.state.filter_label)return!0}else{if(e.label===e.trueLabel)return!1;if("default"===this.state.filter_label)return!0;if(e.trueLabel===this.state.filter_label)return!0}return!1}},{key:"doDownload",value:function(e){console.log("Downloading dataset");var t=e[0].src.split(/(.*)[\/\\]/)[1].split(/(.*)[\/\\]/)[1].split(/(.*)[\/\\]/)[1];console.log("downloadPath: "+t);var n=t.split(/(.*)[\/\\]/)[2];console.log("downloadName: "+n);var c=n+".zip";fetch("/download?dir="+t,{method:"GET",headers:{"Content-Type":"application/octet-stream"}}).then((function(e){return e.blob()})).then((function(e){var t=window.URL.createObjectURL(new Blob([e])),n=document.createElement("a");n.href=t,n.setAttribute("download",c),document.body.appendChild(n),n.click(),n.parentNode.removeChild(n)}))}},{key:"renameSubmit",value:function(e,t){var n=this;console.log("In rename Submit group.");var c={filesrc:e,newtruelabel:t};C.a.post("http://localhost:3001/imagerename",c,{onUploadProgress:function(e){n.setState({loaded:e.loaded/e.total*100})}}).then((function(e){k.b.success("rename success")})).catch((function(e){k.b.error("rename fail")}))}},{key:"deleteImage",value:function(e){var t=this;console.log("In image delete section."),C.a.delete("http://localhost:3001/deletefile?file="+e,{onUploadProgress:function(e){t.setState({loaded:e.loaded/e.total*100})}}).then((function(e){k.b.success("Operation complete!")})).catch((function(e){k.b.error("Operation failed!")}))}},{key:"render",value:function(){var e=this,t=this.state.data;console.log(t);var n=this.getTrueLabels(t);return Object(o.jsxs)("div",{children:[Object(o.jsxs)("div",{className:"stats",children:[Object(o.jsxs)("label",{children:["Total Image Count: ",this.state.TotalImages]}),Object(o.jsx)("br",{}),Object(o.jsxs)("label",{children:["Total Label Count: ",this.state.TotalLabels]}),Object(o.jsx)("br",{}),Object(o.jsxs)("label",{children:["Total Corrected Image Count: ",this.state.TotalCorrections]})]}),Object(o.jsxs)("div",{class:"wrapper",children:[Object(o.jsx)("div",{class:"box",children:Object(o.jsxs)("label",{children:[Object(o.jsx)("input",{type:"checkbox",defaultChecked:this.state.filter,onChange:this.checkFilter,id:"filter"}),"Filter Only Corrected Images"]})}),Object(o.jsx)("div",{class:"box",children:" Filter By Label"}),Object(o.jsx)("div",{class:"box",children:Object(o.jsxs)("select",{id:"label_filter",onChange:this.checkSelectFilter,children:[Object(o.jsx)("option",{value:"default",selected:!0,children:"All"}),n.map((function(e){return Object(o.jsx)("option",{value:e.value,children:e.label})}))]})})]}),Object(o.jsxs)("div",{className:"home",children:[Object(o.jsx)("div",{class:"parent",children:t.map((function(t){return e.canShowImage(t)&&Object(o.jsxs)("div",{class:"child",children:[Object(o.jsx)("img",{src:t.src,alt:""}),Object(o.jsx)("br",{}),"Original Label = ",t.label,Object(o.jsx)("br",{}),"Corrected Label = ",t.trueLabel,Object(o.jsx)("br",{}),Object(o.jsx)("svg",{width:"100%",height:"1",children:Object(o.jsx)("rect",{width:"100%",height:"1"})}),Object(o.jsx)("br",{}),Object(o.jsxs)("div",{children:[Object(o.jsx)(g.a,{options:n,onChange:function(n){return e.renameSubmit(t.src,n.value)}}),Object(o.jsx)("br",{}),Object(o.jsx)("input",{type:"button",class:"myButton1",value:"Delete",id:t.src,onClick:e.deleteImage})]})]})}))}),Object(o.jsx)("input",{type:"button",class:"myButton1",value:"Download",id:"DownloadDataset",onClick:this.doDownload})]})]})}}]),n}(a.a.Component)),T=Object(i.f)(w),L=n(89),S=function(e){Object(u.a)(n,e);var t=Object(h.a)(n);function n(e){var c;return Object(b.a)(this,n),(c=t.call(this,e)).checkMimeType=function(e){for(var t=e.target.files,n=[],c=["image/png","image/jpeg","image/gif","application/zip"],a=0;a<t.length;a++)c.every((function(e){return t[a].type!==e}))&&(n[a]=t[a].type+" is not a supported format\n");for(var l=0;l<n.length;l++)k.b.error(n[l]),e.target.value=null;return!0},c.maxSelectFile=function(e){if(e.target.files.length>4){return e.target.value=null,k.b.warn("Only 4 images can be uploaded at a time"),!1}return!0},c.checkFileSize=function(e){for(var t=e.target.files,n=[],c=0;c<t.length;c++)t[c].size>2e9&&(n[c]=t[c].type+"is too large, please pick a smaller file\n");for(var a=0;a<n.length;a++)k.b.error(n[a]),e.target.value=null;return!0},c.onChangeHandler=function(e){var t=e.target.files;c.maxSelectFile(e)&&c.checkMimeType(e)&&c.checkFileSize(e)&&c.setState({selectedFile:t,loaded:0})},c.onClickHandler=function(){for(var e=new FormData,t=0;t<c.state.selectedFile.length;t++)e.append("file",c.state.selectedFile[t]);C.a.post("http://localhost:3001/upload",e,{onUploadProgress:function(e){c.setState({loaded:e.loaded/e.total*100})}}).then((function(e){k.b.success("upload success")})).catch((function(e){k.b.error("upload fail")}))},c.state={selectedFile:null,loaded:0},c}return Object(j.a)(n,[{key:"render",value:function(){return Object(o.jsx)("div",{class:"container",children:Object(o.jsx)("div",{class:"row",children:Object(o.jsxs)("div",{class:"offset-md-2 col-md-8",children:[Object(o.jsxs)("div",{class:"form-group files",children:[Object(o.jsx)("br",{}),Object(o.jsx)("br",{}),Object(o.jsx)("br",{}),Object(o.jsx)("h4",{children:"Upload Your File "}),Object(o.jsx)("input",{type:"file",class:"form-control",multiple:!0,onChange:this.onChangeHandler})]}),Object(o.jsxs)("div",{class:"form-group",children:[Object(o.jsx)(k.a,{}),Object(o.jsxs)(L.a,{max:"100",color:"success",value:this.state.loaded,children:[Math.round(this.state.loaded,2),"%"]})]}),Object(o.jsx)("button",{type:"button",class:"btn btn-success btn-block",onClick:this.onClickHandler,children:"Upload"}),Object(o.jsx)("br",{}),Object(o.jsx)("a",{type:"button",class:"btn btn-outline-secondary",href:"./",children:"View the Datasets"})]})})})}}]),n}(c.Component);var D=function(){return Object(o.jsx)("div",{className:"App",children:Object(o.jsxs)(r.a,{children:[Object(o.jsx)(d,{}),Object(o.jsxs)(i.c,{children:[Object(o.jsx)(i.a,{path:"/",exact:!0,component:function(){return Object(o.jsx)(f,{})}}),Object(o.jsx)(i.a,{path:"/about",exact:!0,component:function(){return Object(o.jsx)(p,{})}}),Object(o.jsx)(i.a,{path:"/contact",exact:!0,component:function(){return Object(o.jsx)(x,{})}}),Object(o.jsx)(i.a,{path:"/displayimages",exact:!0,component:function(){return Object(o.jsx)(T,{})}}),Object(o.jsx)(i.a,{path:"/uploadimage",exact:!0,component:function(){return Object(o.jsx)(S,{})}})]})]})})},F=function(e){e&&e instanceof Function&&n.e(3).then(n.bind(null,90)).then((function(t){var n=t.getCLS,c=t.getFID,a=t.getFCP,l=t.getLCP,s=t.getTTFB;n(e),c(e),a(e),l(e),s(e)}))};s.a.render(Object(o.jsx)(a.a.StrictMode,{children:Object(o.jsx)(D,{})}),document.getElementById("root")),F()}},[[88,1,2]]]);
//# sourceMappingURL=main.a37554d4.chunk.js.map