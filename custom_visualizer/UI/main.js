import * as THREE from 'three';

const button = document.querySelector(".render-button");

function handleBatch(batch) {
  if (Array.isArray(batch)) {
    for (const gaussian of batch) {
      add_gaussian_to_scene(gaussian);
    }
  } else if (batch && typeof batch === 'object') {
    // Handle single object
    add_gaussian_to_scene(batch);
  } else {
    console.warn('Received batch is neither array nor object:', batch);
  }
}

button.addEventListener("click", () => {

  fetch('http://localhost:5000/data', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: 'Send Gaussians' })
  })
    .then(response => {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      function processText({ done, value }) {
        if (done) {
          if (buffer.trim().length > 0) {
            try {
              const obj = JSON.parse(buffer);
              handleBatch(obj);
            } catch (e) {
              // Ignore trailing blank
            }
          }
          return;
        }
        buffer += decoder.decode(value, { stream: true });
        let lines = buffer.split('\n');
        buffer = lines.pop();
        for (const line of lines) {
          if (line.trim().length > 0) {
            try {
              const obj = JSON.parse(line);

              handleBatch(obj);
            } catch (e) {
              console.error('Error parsing batch:', e, line);
            }
          }
        }
        return reader.read().then(processText);
      }
      return reader.read().then(processText);
    })
    .catch(error => {
      console.error('Streaming error:', error);
    });

});

/////////////////////////////////
// RENDER GAUSSIANS ON SCREEN
/////////////////////////////////

const position = [0, 0, 0];

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.001, 1000);

const ellipsoidPosition = position;

camera.position.set(
  ellipsoidPosition[0] - 0.1,
  ellipsoidPosition[1],
  ellipsoidPosition[2]
);

camera.lookAt(
  ellipsoidPosition[0],
  ellipsoidPosition[1],
  ellipsoidPosition[2]
);

console.log('cam pos');
console.log(camera.position);
console.log(camera.rotation);

const renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
renderer.setAnimationLoop( animate );
document.body.appendChild( renderer.domElement );

function add_gaussian_to_scene(sample_json){
  const material = new THREE.MeshBasicMaterial({ color: 0x00ff00, transparent: true, opacity: sample_json.opacity });
  const ellipsoidGeometry = new THREE.SphereGeometry(1, 32, 32);
  const ellipsoidMesh = new THREE.Mesh(ellipsoidGeometry, material);

  ellipsoidMesh.position.set(
    sample_json.position[0],
    sample_json.position[1],
    sample_json.position[2]
  );

  ellipsoidMesh.scale.set(
    sample_json.scales[0],
    sample_json.scales[1],
    sample_json.scales[2]
  );

  ellipsoidMesh.rotation.set(
    sample_json.rotation[0],
    sample_json.rotation[1],
    sample_json.rotation[2]
  );

  scene.add(ellipsoidMesh);
}

function animate() {

  renderer.render( scene, camera );

}
