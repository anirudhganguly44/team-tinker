import React from "react";
// import { Link } from 'react-router-dom';
// import { DownloadUtil } from '../utils/downloadutil';
import ReactLoading from "react-loading";


class GetDataSets extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      data: [],
      setDone: false,
      setDownloadDone: true
    };
  }

  componentDidMount() {
    setTimeout(() => {
      fetch("/getdatasets?dir=./client/public/selfie-output")
        .then((res) => res.json())
        .then((json) => this.setState({ setDone: true, data: json.express }));
    }, 2000);
  }

  OnClean(dataset) {
    console.log("Cleaning")
    const requestOptions = {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ Dataset: dataset })
    };

    fetch('/train', requestOptions);
    window.location.reload(false);
  }

  OnDownload(dirPath, dirName) {
    console.log("Downloading dataset");
    // DownloadUtil(dirPath, dirName);
    this.setState({ setDownloadDone: false });
    var directoryName = dirName + ".zip";
    setTimeout(() => {
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
          this.setState({ setDownloadDone: true });

          // Append to html link element page
          document.body.appendChild(link);

          // Start download
          link.click();

          // Clean up and remove the link
          link.parentNode.removeChild(link);
        });
    }, 2000);


  }

  render() {
    const datasetList = this.state.data;
    console.log(datasetList);
    const done = this.state.setDone;
    const downloadNotClicked = this.state.setDownloadDone;
    // console.log('Current directory: ' + process.cwd());
    return (

      <div className="wrapper">
        <div class="button_group">
          <a type="button" class="myButton4" href="./uploadimage">Upload</a>
          <a type="button" class="myButton4" href="./create">Create</a>
        </div>
        <div>
        {!downloadNotClicked ? (
                <ReactLoading className="loadercenter"
                  type={"bars"}
                  color={"#03fc4e"}
                  height={50}
                  width={50}
                />
              ) : (
                <br/>
              )}
        </div>
        {!done ? (
          <ReactLoading className="loadercenter"
            type={"bars"}
            color={"#03fc4e"}
            height={100}
            width={100}
          />
        ) : (
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
                      <div style={{ 'text-transform': 'uppercase' }}>
                        {dataset.status === "clean" &&
                          <a className="hyperlink" href={"/displayimages?name=" + dataset.name}> <div>{dataset.name}</div> </a>
                        }
                        {dataset.status !== "clean" &&
                          <a> <div>{dataset.name}</div> </a>
                        }

                      </div>
                    </td>
                    <td style={{ 'text-transform': 'uppercase' }}>{dataset.status}
                    </td>
                    <td width="auto">
                      {dataset.status === "clean" &&
                        <input type="button" class="myButton1" onClick={() => this.OnDownload(dataset.path, dataset.name)} value="Download" id={dataset.name} />
                      }
                      {dataset.status === "clean" &&
                        <input type="button" class="myButton1" onClick={() => this.OnClean(dataset.name)} value="Clean" id={dataset.name} disabled />
                      }
                      {dataset.status === "unclean" &&
                        <input type="button" class="myButton1" onClick={() => this.OnDownload(dataset.path, dataset.name)} value="Download" id={dataset.name} disabled />
                      }
                      {dataset.status === "unclean" &&
                        <input type="button" class="myButton1" onClick={() => this.OnClean(dataset.name)} value="Clean" id={dataset.name} />
                      }
                      {dataset.status === "inprogress" &&
                        <ReactLoading
                          type={"bars"}
                          color={"#03fc4e"}
                          height={25}
                          width={25}
                        />
                      }
                    </td>
                  </tr>
                ))
              }
            </tbody>
          </table>
        )}
      </div>
    );
  }
}

export default GetDataSets;
