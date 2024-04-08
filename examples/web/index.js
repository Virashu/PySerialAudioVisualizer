const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}

resizeCanvas();
window.addEventListener('resize', resizeCanvas, false);

const render = (data) => {
  context.clearRect(0, 0, canvas.width, canvas.height);

  let k = 10
  let w = canvas.width / data.length;
  let cy = canvas.height;

  data.forEach((l, i) => {
    let h = l * k;
    let x = i * w;
    let y = cy - h;

    context.fillStyle = `#fff`;
    context.beginPath();
    context.roundRect(x, y, w, h, 5);
    context.fill();
  });
}

const update = () => {
  fetch("http://127.0.0.1:7777")
    .then((res) => res.json())
    .then((res) => (res ? render(res.data) : ""));
}

setInterval(update, 10);
