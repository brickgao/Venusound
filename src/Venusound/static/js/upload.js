function fileSelected() {
  var file = document.getElementById('fileToUpload').files[0];
  if (file) {
    var fileSize = 0;
    if (file.size > 1024 * 1024)
      fileSize = (Math.round(file.size * 100 / (1024 * 1024)) / 100).toString() + 'MB';
    else
      fileSize = (Math.round(file.size * 100 / 1024) / 100).toString() + 'KB';
    document.getElementById('fileName').innerHTML = '文件名：' + file.name;
    document.getElementById('fileSize').innerHTML = '文件大小：' + fileSize;
    document.getElementById('fileType').innerHTML = '文件类型：' + file.type;
    setProcess('0');
    }
}

function uploadFile() {
    var file = document.getElementById('fileToUpload').files[0]
    var file_name = document.getElementById('fileName').innerHTML
    var file_size = document.getElementById('fileSize').innerHTML
    var file_type = document.getElementById('fileType').innerHTML
    var process = document.getElementById('processPercent').innerHTML
    if(!file || (file_name == "FileName: ") || (file_size == "FileSize: ")){
      alert('请选择文件');
    }
    else if(process == "上传进度：100%"){
      alert('请重新选择文件');
    }
    else{
      var fd = new FormData();
      fd.append("file", file);
      var xhr = new XMLHttpRequest();
      xhr.upload.addEventListener("progress", uploadProgress, false);
      xhr.addEventListener("load", uploadComplete, false);
      xhr.addEventListener("error", uploadFailed, false);
      xhr.addEventListener("abort", uploadCanceled, false);
      xhr.open("POST", "", true);
      xhr.send(fd);
  }
}

function uploadProgress(evt) {
  if(evt.lengthComputable) {
    var percentComplete = Math.round(evt.loaded * 100 / evt.total);
    setProcess(percentComplete.toString());
  }
  else {
    document.getElementById('progressNumber').innerHTML = '无法完成';
  }
}

function uploadComplete(evt) {
  setProcess(100);
  location.reload()
    //document.getElementById('success-msg').innerHTML = evt.target.responseText
    //$("#success-bar").show()
}

function uploadFailed(evt) {
  alert("上传文件错误");
}

function uploadCanceled(evt) {
  alert("上传文件被终止");
}

function setProcess(percent) {
  document.getElementById('processPercent').innerHTML = '上传进度：' + percent + '%';
  document.getElementById('progressNumber').innerHTML =
      '<div class="progress-bar" align = "middle" style="width: ' +
      percent + '%;">' + '</div>';
}

