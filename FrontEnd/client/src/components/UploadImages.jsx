// import React, { useState } from "react";

// function UploadImages (props) {
//   const [data, setData] = useState([]);
//   const [loaderOn, setLoaderOn] = useState(false);
//   const [files, setFiles] = useState(null);
//   const [imageURL, setImageURL] = useState(null);

//   const onImageChange = e => { 
//     setFiles(e.target.files[0]);
//   }

//   const loadImages = (e) => {
 
//     const { files } = e.target
//     if (files.length > 0) {
//         const url = URL.createObjectURL(files[0])
//         setImageURL(url)
//     } else {
//         setImageURL(null)
//     }   
//   }

//   // onFormSubmit(e){
//   //     e.preventDefault();
//   //     const formData = new FormData();
//   //     formData.append('myImage',this.state.file);
//   // }

//     return (
//       <div className="home">
//         {/* <script src="../dist/zip-loader.js"></script> */}
//         <div>   
//           {/* <form onSubmit={this.onFormSubmit}> */}
//               {/* <h4>File Upload</h4> */}
//               <input type="file" name="myImage" onChange={onImageChange} />
//               {/* <button type="submit">Load Images</button> */}
//               <button className='button' onClick={loadImages}>Load Images</button>
//           {/* </form> */}
//         </div>
//       </div> 
//     );
// }

// // React.Dom.render(
// //   document.getElementById( 'button' ).addEventListener( 'click', function ( e ) 
// //     {
// //       loader.loadimages();
// //       e.target.disabled = true;
  
// //     } ));

// export default UploadImages;
