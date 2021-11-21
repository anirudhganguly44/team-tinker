import React from "react";
// import { Link } from 'react-router-dom';
// import { DownloadUtil } from '../utils/downloadutil';

class GetDataSets extends React.Component {

  constructor(props) {
    super(props);
    this.state = { data: [] };
  }

  componentDidMount() {
    fetch("/getdatasets?dir=./client/public/selfie-output")
      .then((res) => res.json())
      .then((json) => this.setState({ data: json.express }));
  }

  OnClean(dataset) {
    console.log("Cleaning")
    const requestOptions = {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ Dataset: dataset })
    };

    fetch('/train', requestOptions)
  }

  OnDownload(dirPath, dirName) {
    console.log("Downloading dataset");
    // DownloadUtil(dirPath, dirName);

    var directoryName = dirName + ".zip";
    fetch('/download?dir=' + dirPath, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/octet-stream',
      },
    })
      .then((response) => response.blob())
      .then((blob) => {
        // Create blob link to download
        const url = window.URL.createObjectURL(
          new Blob([blob]),
        );
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute(
          'download',
          directoryName,
        );

        // Append to html link element page
        document.body.appendChild(link);

        // Start download
        link.click();

        // Clean up and remove the link
        link.parentNode.removeChild(link);
      });


  }

  render() {
    const datasetList = this.state.data;
    // console.log(datasetList);
    // console.log('Current directory: ' + process.cwd());
    return (


      <div className="wrapper">
        <div class="button_group">
        <a  type="button" class="myButton4" href="./uploadimage">Upload</a> 
        <a type="button" class="myButton4" href="./create">Create</a>
        </div>
        <table className="table blueTable">
          <thead>
            <tr>
              <th>Dataset</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {
              datasetList.map((dataset) => (
                <tr>
                  <td>
                      {/* <Link
                        to={{
                          pathname: '/displayimages?name=' + dataset.name
                        }}
                      >{dataset.name}
                      </Link> */}
                      <div style={{ 'text-transform': 'uppercase' }}>
                      <a className="hyperlink" href={"/displayimages?name=" + dataset.name}> <div>{dataset.name}</div> </a>
                      </div>
                  </td>
                  <td style={{ 'text-transform': 'uppercase' }}>{dataset.status}
                  </td>
                  <td width="auto">
                    {dataset.status === "clean" &&
                      <input type="button" class="myButton1" onClick={() => this.OnDownload(dataset.path, dataset.name)} value="Download" />
                    }
                    {dataset.status === "clean" &&
                      <input type="button" class="myButton1" onClick={() => this.OnClean(dataset.name)} value="Clean" disabled />
                    }
                    {dataset.status === "unclean" &&
                      <input type="button" class="myButton1" onClick={() => this.OnDownload(dataset.path, dataset.name)} value="Download" disabled />
                    }
                    {dataset.status === "unclean" &&
                      <input type="button" class="myButton1" onClick={() => this.OnClean(dataset.name)} value="Clean" />
                    }
                  </td>
                </tr>
              ))
            }
          </tbody>
        </table>
      </div>
    );
  }
}

export default GetDataSets;
