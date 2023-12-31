// iframe에 cctv api_url 입력하여 video 생성하는 함수. 사용 안 함
function setIframeSrc() {
    const api_url = 'http://www.utic.go.kr/view/map/cctvStream.jsp?cctvid=L902704&cctvname=%25EC%2584%259C%25EC%259A%25B8%2520%25EC%2584%259C%25EC%25B4%2588%2520%25EC%2584%259C%25EC%25B4%2588%25EB%258C%2580%25EB%25A1%259C&kind=EE&cctvip=9990&cctvch=null&id=null&cctvpasswd=null&cctvport=null&minX=127.00182995981353&minY=37.48782667683961&maxX=127.06121163497251&maxY=37.51313060242616' + '?time=' + new Date().valueOf()
    const cctvContainer = document.getElementById("cctvContainer");
    const iframe = document.createElement("iframe");
    iframe.src = api_url;
    iframe.width = "1000";
    iframe.height = "1000";
    iframe.setAttribute("allowfullscreen", "");
    iframe.setAttribute("id", "ifif");
    iframe.setAttribute("crossorigin", "anonymous");
    cctvContainer.appendChild(iframe);
    // iframe이 로드될 때까지 기다리기 (옵션)
    iframe.onload = function() {
        // iframe 내부의 Window 객체 가져오기
        var iframeWindow = iframe.contentWindow;

        // iframe 내부의 document 가져오기
        var iframeDocument = iframeWindow.document;

        // #document 내부의 video 요소 가져오기
        var videoElement = iframeDocument.querySelector("video");

        console.log(videoElement);
    };
};

// video, 모델 결과 표기하는 div
// const view = document.getElementById('view')
const names = 
    ['오토바이','오토바이 보행자도로 통행','오토바이 안전모 미착용','오토바이 무단횡단','오토바이 신호 위반','오토바이 정지선 위반','오토바이 횡단보도 주행',
    '자전거','자전거 캐리어','자전거 보행자도로 통행','자전거 안전모 미착용','자전거 무단 횡단','자전거 신호 위반','자전거 정지선 위반','자전거 횡단보도 주행',
    '킥보드','킥보드 캐리어','킥보드 보행자도로 통행','킥보드 안전모 미착용','킥보드 무단 횡단','킥보드 신호 위반','킥보드 횡단보도 주행','킥보드 동승자 탑승'];
const goodLabels = [0,7,8,15,16]; // 오토바이, 자전거, 킥보드, 캐리어 등 위반 안 한 PM index

// 학습 데이터 원본 이미지 비율. 이것으로 예측 데이터 이미지 비율 조정 필요
const aspectRatio = 16/9
const [inputWidth, inputHeight] = [640, 640];

// 입력한 frame마다 pm 담아두는 변수
var spmsHolder = []; // 비디오에 표기할 pm 담아두는 변수 (s: screen)
var lpmsHolder = []; // 저장용 캔버스에 표기할 pm 담아두는 변수 (l: log)
let canvasHolder; // 저장용 캔버스 담아두는 변수

// yolov5 모델 함수
let yolov5 = null;
const square = false;
async function loadModel() {
    try {
        const yolov5 = await tf.loadGraphModel('/static/TfjsYolov5Det/model.json');

        return yolov5;
    } catch (error) {
        console.error("Error:", error);
        return null;
    }
}
// 모델 로드되면 yolov5에 저장
loadModel().then(model => {
    yolov5 = model;
    // 3초 기다렸다가 실행. videoWidth, videoHeight가 0이 아닌 경우 .then하는 것 나중에 적용해보기
    setTimeout(function() {
        setInterval(predict, 100);
    }, 500);
})

// video에서 원본 frame 추출
function getOriginalVideoFrame(video) {
    let width, height;
    if (video.tagName == 'VIDEO') { // video
        width = video.videoWidth;
        height = video.videoHeight;
    }
    else { // 테스트용 이미지
        width = video.naturalWidth;
        height = video.naturalHeight;
    }
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d', {willReadFrequently: true});
    ctx.drawImage(video, 0, 0, width, height);
    return [ctx.getImageData(0, 0, width, height), width, height];
}

async function predict() {
    tf.engine().startScope(); // endScope까지 생성된 tensor 메모리에서 삭제
    // const inputImage = document.getElementById("inputImage"); // 이미지는 테스트용
    // const inputImage = document.getElementById("inputVideo"); // 비디오 테스트용
    // const inputImage = document.getElementById("inputVideo_html5_api"); // m3u8 id
    // const inputImage = document.querySelector("video"); // id와 상관 없이 video
    let inputImage;
    if (document.querySelector('video')) {
        inputImage = document.querySelector("video"); // id와 상관 없이 video
    }
    else {
        inputImage = document.getElementById('inputImage'); // 테스트용 이미지
    }
    
    // 원본/화면에 보이는 비디오 사이즈 파악 및 프레임 추출
    const [imageData, originalImageWidth, originalImageHeight] = getOriginalVideoFrame(inputImage);
    const screenImageWidth = inputImage.clientWidth;
    const screenImageHeight = inputImage.clientHeight;
    const currentTimestamp = Date.now(); // 추출한 시각
    const input = tf.browser.fromPixels(imageData).div(255.0);
    let rescaledInput;
    
    // 사이즈 조정 단계.
    // 0. cropBox에 따라 잘라주기
    // 1. 정사각형 학습 모델은 16:9 비율로 현 이미지 세로 늘려줌.
    // 2. padding으로 정사각형으로 만듦
    // 3. 640x640로 resize

    // 0. crop
    const screenCropBox = document.getElementById('screenCropBox');
    // 기본 view 사이즈
    const cropStyle = screenCropBox.style.cssText;
    // 화면에 보이는 cropBox 사이즈
    const screenCropLeft = Math.round(screenCropBox.getAttribute('data-x'));
    const screenCropTop = Math.round(screenCropBox.getAttribute('data-y'));
    const screenCropWidth = Math.round(cropStyle.match(/width:\s*([\d.]+)px/)[1]);
    const screenCropHeight = Math.round(cropStyle.match(/height:\s*([\d.]+)px/)[1]);
    const widthFactor = originalImageWidth / screenImageWidth;
    const heightFactor = originalImageHeight / screenImageHeight
    // 입력할 cropBox 사이즈
    const realCropLeft = Math.round(screenCropLeft*widthFactor);
    const realCropTop = Math.round(screenCropTop*heightFactor);
    const realCropWidth = Math.round(screenCropWidth*widthFactor);
    const realCropHeight = Math.round(screenCropHeight*heightFactor);
    if (realCropLeft+realCropWidth > originalImageWidth) {
        realCropWidth = originalImageWidth-realCropLeft;
    }
    if (realCropTop+realCropHeight > originalImageHeight) {
        realCropHeight = originalImageHeight-realCropTop;
    }
    // slice에 입력할 array
    let cropStartPoint = [realCropTop, realCropLeft, 0]; // top, left, r (rgb의 r)
    let cropSize = [realCropHeight, realCropWidth, 3];
    rescaledInput = tf.slice(input, cropStartPoint, cropSize);

    // 1. 비율 늘려주기
    let intermediateHeight;
    if (square) {
        intermediateHeight = Math.round(realCropHeight * aspectRatio);
        rescaledInput = tf.image.resizeBilinear(rescaledInput, [intermediateHeight, realCropWidth], true);
    }
    else {
        intermediateHeight = realCropHeight;
    }

    // 2. padding
    let padAmount;
    if (intermediateHeight > realCropWidth) { // 현재 이미지 height과 width 비교해서 이미지 padding 결정. y가 더 긺
        padAmount = intermediateHeight - realCropWidth;
        rescaledInput = rescaledInput.pad([
            [0,0],
            [0, padAmount],
            [0,0]
        ]);
    }
    else if (intermediateHeight < realCropWidth) { // x가 더 긺
        padAmount = realCropWidth - intermediateHeight;
        rescaledInput = rescaledInput.pad([
            [0, padAmount],
            [0,0],
            [0,0]
        ]);
    }
    // crop에 표기할 bounding box 표기할 비율 계산. pad하기 때문에 늘어난 비율만큼 cropBox에 적용해야 함
    const [paddedHeight, paddedWidth] = rescaledInput.shape;
    const padFactorX = paddedWidth / realCropWidth;
    const padFactorY = paddedHeight / intermediateHeight;
    const screenCropHiddenWidth = screenCropWidth * padFactorX;
    const screenCropHiddenHeight = screenCropHeight * padFactorY;
    const realCropHiddenWidth = realCropWidth * padFactorX;
    const realCropHiddenHeight = realCropHeight * padFactorY;

    // 3. resize
    rescaledInput = tf.image.resizeBilinear(rescaledInput, [inputWidth, inputHeight], true).expandDims(0); // yolo inputsize에 맞게 batchSize dimension 추가해주기
    
    // Make predictions using the yolov5 model
    const predictions = await yolov5.executeAsync(rescaledInput);
    const [bboxes, scores, labels, valid_detections] = predictions;
    
    // drawBb에는 tensor 전달 안 하기. array로 저장
    const bboxes_data = Array.from(bboxes.dataSync());
    const scores_data = Array.from(scores.dataSync());
    const labels_data = Array.from(labels.dataSync());
    const valid_detections_data = valid_detections.dataSync()[0];

    console.log(valid_detections_data)
    // 모델 한 번 입력시키고 화면에 그려줄지 확인하는 단계에서 이미 그려져 있는 부분 지우기
    deletePms(spmsHolder, view);

    // valid_detections가 있을 때에만, 즉 detection이 있는 경우 이후 과정 수행
    if (valid_detections_data > 0) {
        // bboxes_data는 1차원 배열. 4개의 요소를 가지는 valid_detection_data개의 배열로 재정렬
        const screen_bboxes = []; // 표기
        const drawing_bboxes = []; // 화면 표기
        const log_bboxes = []; // 로그/저장
        for (let i = 0; i < valid_detections_data; i += 1) {
            let [x1, y1, x2, y2] = bboxes_data.slice(i * 4, (i + 1) * 4);
            if (x1 < 0) {x1 = 0}
            if (y1 < 0) {y1 = 0}
            if (x2 > 1) {x2 = 1}
            if (y2 > 1) {y2 = 1}
            let sX1 = (x1*screenCropHiddenWidth) + screenCropLeft;
            let sX2 = (x2*screenCropHiddenWidth) + screenCropLeft;
            let sY1 = (y1*screenCropHiddenHeight) + screenCropTop;
            let sY2 = (y2*screenCropHiddenHeight) + screenCropTop;
            let sWidth = sX2 - sX1;
            let sHeight = sY2 - sY1;
            let dX1 = (x1*realCropHiddenWidth) + realCropLeft;
            let dX2 = (x2*realCropHiddenWidth) + realCropLeft;
            let dY1 = (y1*realCropHiddenHeight) + realCropTop;
            let dY2 = (y2*realCropHiddenHeight) + realCropTop;
            let dWidth = dX2 - dX1;
            let dHeight = dY2 - dY1;
            let lX1 = sX1 / screenImageWidth;
            let lX2 = sX2 / screenImageWidth;
            let lY1 = sY1 / screenImageHeight;
            let lY2 = sY2 / screenImageHeight;
            let lWidth = lX2 - lX1;
            let lHeight = lY2 - lY1;
            let lXC = (lX1+lX2) / screenImageWidth;
            let lYC = (lY1+lY2) / screenImageHeight
            screen_bboxes.push([sX1, sY1, sWidth, sHeight]);
            drawing_bboxes.push([dX1, dY1, dWidth, dHeight]);
            log_bboxes.push([lXC, lYC, lWidth, lHeight]);
        }

        const scores = scores_data.slice(0,valid_detections_data);
        const labels = labels_data.slice(0,valid_detections_data);

        // 그리기
        drawBoundingBoxes(screen_bboxes, scores, labels, spmsHolder, view);

        // 위반사항 아닌 경우 로그 남기지 않기 위한 계산
        const filteredLogBboxes = [];
        const filteredDrawingBboxes = [];
        const filteredScores = [];
        const filteredLabels = [];
        const filterCheck = [];
        for (let i = 0; i < labels.length; i++) {
            const label = labels[i];
            if (!goodLabels.includes(label)) {
                filteredDrawingBboxes.push(drawing_bboxes[i]);
                filteredLogBboxes.push(log_bboxes[i]);
                filteredScores.push(scores[i]);
                filteredLabels.push(label);
                filterCheck.push(1); // 위반
            }
            else {
                filterCheck.push(0); // 위반 아님
            }
        }
        
        // let filePath = null;
        let imgName = null;
        // 재정렬한 labels length 0보다 크면, 즉 위반한 객체가 있으면
        if (filteredLabels.length > 0) {
            // 이미지 저장
            // const fileName = cctvName + '_' + currentTimestamp + '.jpg'
            // filePath = 'C:/cctv_images/' + fileName
            imgName = cctvName + '_' + currentTimestamp + '.jpg'
            // saveImage(imageData, drawing_bboxes, scores, labels, fileName); // 저장할 때는 정상 객체도 표기
            saveImage(imageData, filteredDrawingBboxes, filteredScores, filteredLabels, imgName); // 저장할 때 정상 객체도 제외
        }
        // 저장/표기할 로그 생성
        const [dbLogItems, screenLogItems] = log(log_bboxes, scores, labels, currentTimestamp, originalImageWidth, originalImageHeight, imgName, filterCheck);
        for (let i = 0; i < screenLogItems.length; i += 1) {
            // 로그 표기
            updateScreenLogs(screenLogItems[i]);
        }

        // 로그 저장
        sendPostRequest(dbLogItems)

    }
    tf.engine().endScope(); // scope 사이 생성된 tensor 메모리에서 삭제
}

// 저장할 이미지 그리는 함수
async function drawBoundingBoxesToSave(imageData, bboxes, scores, labels) {
    const div = document.getElementById('outputImage');
    deletePms(lpmsHolder, div); // 저장용 canvas 관리
    if (!canvasHolder) {
        const canvas = document.createElement("canvas");
        canvasHolder = canvas;
        const width = imageData.width;
        const height = imageData.height;
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d", {willReadFrequently: true});
        ctx.putImageData(imageData, 0, 0);
    }

    const canvas = canvasHolder;
    const width = imageData.width;
    const height = imageData.height;
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d", {willReadFrequently: true});

    // 이미지 그리기
    ctx.putImageData(imageData, 0, 0);

    // div에 추가
    div.appendChild(canvas);

    // bounding box 그리고 div에 추가해서 div return
    return drawBoundingBoxes(bboxes, scores, labels, lpmsHolder, div);
}

// 이미지와 bounding box 정보를 받아 JPG 파일로 저장합니다.
async function saveImage(image, bboxes, scores, labels, imgName) {
    const div = await drawBoundingBoxesToSave(image, bboxes, scores, labels);
    html2canvas(div).then(canvas => {
        if (navigator.msSaveBlob) {
        var blob = canvas.msToBlob(); 
        return navigator.msSaveBlob(blob, fileName); 
        } else { 
        var el = document.getElementById("target");
        el.href = canvas.toDataURL("image/jpeg");
        el.download = imgName;
        el.click();
        }
    });
}

// pm 요소 삭제하는 함수. 비디오에 그릴때랑 저장하는 canvas에 그릴 때 각각 사용
function deletePms(pmsHolder, divTag) {
    // html에서 pm 지우기
    for (let i=0; i < pmsHolder.length; i++) {
        divTag.removeChild(pmsHolder[i])
    }
    // pmsHolder에서 pm 지우기
    pmsHolder.splice(0);
}

// 비디오에 그리는 함수
function drawBoundingBoxes(bboxes, scores, labels, pmsHolder, divTag) {
    // bbox마다
    for (let n=0; n < bboxes.length; n++) {
        // label
        const labelDiv = document.createElement('div');
        labelDiv.setAttribute('class', 'labelDiv');
        labelDiv.style = 'left: ' + bboxes[n][0] + 'px; top: ' +
            (bboxes[n][1]-20) + 'px; width: ' +
            bboxes[n][2] + 'px; height: ' +
            20 + 'px;'
        const label = document.createElement('p');
        label.innerText = labels[n]
        label.style = 'width: ' + bboxes[n][2] + 'px;'
        labelDiv.appendChild(label)
        // bbox
        const drawing = document.createElement('div');
        drawing.setAttribute('class', 'drawing');
        drawing.style = 'left: ' + bboxes[n][0] + 'px; top: ' +
            bboxes[n][1] + 'px; width: ' +
            bboxes[n][2] + 'px; height: ' +
            bboxes[n][3] + 'px;'
        divTag.appendChild(drawing);
        divTag.appendChild(labelDiv);
        pmsHolder.push(drawing);
        pmsHolder.push(labelDiv);
    }
    return divTag;
}

// 로그 생성 함수
function log(bboxes, scores, labels, timestamp, width, height, imgName, filterCheck) {
    const dbLogItems = [];
    const screenLogItems = [];
    for (let i = 0; i < bboxes.length; i += 1) {
        let [lBboxWidth, lBboxHeight] = bboxes[i].slice(2,4);
        let dbXCenter = bboxes[i][0] + lBboxWidth/2;
        let dbYCenter = bboxes[i][1] + lBboxHeight/2;
        let sXCenter = dbXCenter.toFixed(4);
        let sYCenter = dbYCenter.toFixed(4);

        let dbScore = scores[i];
        let lLabel = labels[i];
        let sScore = dbScore.toFixed(4);

        let lImgName = filterCheck[i] ? imgName : null; // ternery

        let date = new Date(timestamp);
        let year = date.getFullYear();
        let month = String(date.getMonth() + 1).padStart(2,0);
        let day = String(date.getDate()).padStart(2,0);
        let hours = String(date.getHours()).padStart(2,0);
        let minutes = String(date.getMinutes()).padStart(2,0);
        let seconds = String(date.getSeconds()).padStart(2,0);
        let subseconds = String(Math.round((timestamp%1000)/10)).padStart(2,0);
        let dateString = `${year}-${month}-${day}`
        let timeString = `${hours}:${minutes}:${seconds}:${subseconds}`

        let dbDatapoint = {
            'cctvId': cctvId, 
            'cctvName': cctvName, 
            'centerName': centerName, 
            'timestamp': timestamp, 
            'xCenter': dbXCenter, 
            'yCenter': dbYCenter, 
            'bWidth': lBboxWidth, 
            'bHeight': lBboxHeight, 
            'iWidth': width, 
            'iHeight': height, 
            'score': dbScore, 
            'label': lLabel, 
            'imgName': lImgName
        };
        let screenDatapoint = [dateString, timeString, sXCenter, sYCenter, sScore, lLabel, lImgName];
        dbLogItems.push(dbDatapoint);
        screenLogItems.push(screenDatapoint)
    }
    return [dbLogItems, screenLogItems];
}

// 화면에 로그 표기
const displayExcludeArray = ['cctvId', 'cctvName', 'centerName', 'bWidth', 'bHeight', 'iWidth', 'iHeight']
const logKeys = ['cctvId', 'cctvName', 'centerName', "timestamp", "xCenter", "yCenter", "bWidth", "bHeight", "iWidth", "iHeight", "score", "label", 'imgName'];
var deleteEmptyRow = 1;
function updateScreenLogs(screenLogItem) {
    const table = document.getElementById('logTable');
    if (table.rows.length == 2 && deleteEmptyRow) {
        table.deleteRow(-1);
        deleteEmptyRow = 0;
    }
    const row = table.insertRow();
    for (let i = 0; i < screenLogItem.length; i += 1) {
        let cell = row.insertCell(i);
        cell.innerText = screenLogItem[i];
    }
}

async function sendPostRequest(dbLogItems) {
    // POST 요청을 보냅니다.
    fetch('/detect_post', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dbLogItems)
        })
        .then(response => response.text())
        .then(result => console.log(result))
        .catch(error => console.error(error));
}
