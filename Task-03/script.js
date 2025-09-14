const canvas = document.querySelector("canvas");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const centreX = canvas.width / 2;
const centreY = canvas.height / 2;

let isDrawing = false;
let lastX = 0;
let lastY = 0;
let points = [];
let score = 0;   

// draw red center dot + score
function drawCenterDot() {
  ctx.fillStyle = "red";
  ctx.beginPath();
  ctx.arc(centreX, centreY, 5, 0, Math.PI * 2);
  ctx.fill();

  // show score in the middle
  ctx.fillStyle = "black";
  ctx.font = "36px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline ="middle";
  ctx.fillText("Score: " + score.toFixed(2) + " / 100", canvas.width / 2, canvas.height / 2);
}

drawCenterDot();

// drawing settings
ctx.strokeStyle = "black";
ctx.lineWidth = 2;
ctx.lineJoin = "round";
ctx.lineCap = "round";

canvas.addEventListener("mousedown", function(e) {
  isDrawing = true;
  points = []; 
  lastX = e.offsetX - centreX;
  lastY = e.offsetY - centreY;
  points.push([lastX, lastY]);
});

canvas.addEventListener("mousemove", function(e) {
  if (!isDrawing) return;

  let x = e.offsetX - centreX;
  let y = e.offsetY - centreY;

  ctx.beginPath();
  ctx.moveTo(lastX + centreX, lastY + centreY);
  ctx.lineTo(x + centreX, y + centreY);
  ctx.stroke();

  lastX = x;
  lastY = y;
  points.push([x, y]);
});

canvas.addEventListener("mouseup", function() {
  isDrawing = false;
  evaluateCircle(points);
});

canvas.addEventListener("mouseout", function() {
  isDrawing = false;
});

function evaluateCircle(points) {
  if (points.length < 10) return; 


  let sumX = 0;
  let sumY = 0;
  for (let i = 0; i < points.length; i++) {
    sumX += points[i][0];
    sumY += points[i][1];
  }
  let avgX = sumX / points.length;
  let avgY = sumY / points.length;

  
  let radii = [];
  for (let i = 0; i < points.length; i++) {
    let dx = points[i][0] - avgX;
    let dy = points[i][1] - avgY;
    radii.push(Math.sqrt(dx * dx + dy * dy));
  }

  //  radius
  let sumR = 0;
  for (let i = 0; i < radii.length; i++) {
    sumR += radii[i];
  }
  let avgRadius = sumR / radii.length;

  // deviation
  let deviations = [];
  for (let i = 0; i < radii.length; i++) {
    deviations.push(Math.abs(radii[i] - avgRadius));
  }

  let sumDev = 0;
  for (let i = 0; i < deviations.length; i++) {
    sumDev += deviations[i];
  }
  let avgDeviation = sumDev / deviations.length;

  // score out of 100
  score = 100 - avgDeviation;
  if (score < 0) score = 0;

  // clear e
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // redraw center + score
  drawCenterDot();
}
