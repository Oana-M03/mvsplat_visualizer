import * as THREE from 'three';
import { AxesHelper } from 'three';

var mesh_IDs = [];
var options = {};

///////////////////////////////////
////////// UI-RELATED FUNCTIONALITY
/////////////////////////////////////

function switchOptions(){
  var checkboxes = document.querySelectorAll(".option");
  console.log(checkboxes.length);
  checkboxes.forEach(checkbox => {
    console.log(checkbox.id);
    console.log(checkbox.checked)
    options[checkbox.id] = checkbox.checked;
  });
}

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

const button = document.querySelector(".render-button");
button.addEventListener("click", () => {

  scene_cleanup();

  switchOptions();

  fetch('http://localhost:5000/data', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: options })
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

var position = [0, 0, 0];
var len = 0;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff); // set background color to white

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.001, 1000);
camera.position.set(-0.1, -0.1, -0.3);

const axesHelper = new AxesHelper(2);
scene.add(axesHelper);

const renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
renderer.setAnimationLoop( animate );
document.body.appendChild( renderer.domElement );

function add_gaussian_to_scene(sample_json){

  const color = new THREE.Color(0, 255 * sample_json.opacity, 0);
  var material = new THREE.MeshBasicMaterial({ color: color, transparent: false, opacity: sample_json.opacity });

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

  mesh_IDs.push(ellipsoidMesh.uuid);

  // Change position of camera and light

  position[0] = (position[0] * len + sample_json.position[0]) / (len + 1);
  position[1] = (position[1] * len + sample_json.position[1]) / (len + 1);
  position[2] = (position[2] * len + sample_json.position[2]) / (len + 1);
  len = len + 1;

}

function scene_cleanup(){
  mesh_IDs.map(id =>{
    var mesh = scene.getObjectByProperty('uuid', id);
    mesh.geometry.dispose();
    mesh.material.dispose();
    scene.remove(mesh);
  });
  renderer.renderLists.dispose();
  mesh_IDs = [];
}

function animate() {

  camera.lookAt(position[0], position[1], position[2]);

  renderer.render( scene, camera );

}
