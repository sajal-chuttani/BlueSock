
const uploadBttn = document.getElementById('upload-bttn');
const fileInput = document.getElementById('files');

uploadBttn.disable = true;
uploadBttn.style.backgroundColor = '#AAAAAA';


const checkTotalFileSize = () => {
    const allFiles = [...fileInput.files];
    let totalsize = 0;
    for (let i = 0; i < allFiles.length; i++) {
        totalsize += allFiles[i].size;
    }
    if (totalsize === 0) return;
    if (totalsize > 41943040) {
        alert('Total file size exceeds 40MB limit.')
    } else {
        uploadBttn.disabled = false;
        uploadBttn.style.backgroundColor = '#0B5ED7';
    }
}


if (fileInput) {
    fileInput.addEventListener('change', checkTotalFileSize);
}
