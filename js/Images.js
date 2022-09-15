var targetImg = document.getElementById('Image');
var orgWidth  = targetImg.width;  // 元の横幅を保存
var orgHeight = targetImg.height; // 元の高さを保存
targetImg.width = 400;  // 横幅を400pxにリサイズ
targetImg.height = orgHeight * (targetImg.width / orgWidth); // 高さを横幅の変化割合に合わせる