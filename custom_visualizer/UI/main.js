import * as THREE from 'three';
import { AxesHelper } from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

var mesh_IDs = [];
var options = {};
var image_blobs = [];
let currIndex = 0;

/////////////////////////////////////
/////////// UI-RELATED FUNCTIONALITY
/////////////////////////////////////

function switchOptions(){
  var checkboxes = document.querySelectorAll(".option");
  checkboxes.forEach(checkbox => {
    options[checkbox.id] = checkbox.checked;
  });
}

function handleBatch(batch) {

  if (options['vis_choice'] == 'gaussians'){
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
  
}

const radio_div = document.querySelector(".scene-choice");

radio_div.addEventListener('change', event =>{
  if(event.target.type == 'radio' && event.target.name == 'vis_pref'){
    options['vis_choice'] = event.target.value;

    if(event.target.value == 'images'){
      document.querySelector(".show-images").style.display = 'block';
      document.querySelector(".checkbox-container").style.display = 'none';
      scene_cleanup();
      hide_scene();
    } else if(event.target.value == 'video'){
      document.querySelector(".show-images").style.display = 'none';
      document.querySelector(".checkbox-container").style.display = 'block';
      scene_cleanup();
      hide_scene();
    } else{
      document.querySelector(".show-images").style.display = 'none';
      document.querySelector(".checkbox-container").style.display = 'block';
      show_scene();
    }

  }
});

const button = document.querySelector(".render-button");

function fetch_gaussians(){
  fetch('http://localhost:5000/gaussians', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
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
}

function fetch_image(index){
  fetch('http://localhost:5000/images', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ index : index })})
    .then(response => response.blob())
    .then(blob =>{
      document.querySelector('#main-image').src = URL.createObjectURL(blob);
    }
  );
} 


function fetch_video(){
  fetch('http://localhost:5000/video', {
    method: 'POST',
    headers: {
      'Content-type': 'application/json',
    },
    body: JSON.stringify({message: options})
  })
  .then(response => {
    const path = response.json()['message'];
    const video_div = document.querySelector('#real-video-player');
    video_div.src = path;
  });
}

button.addEventListener("click", () => {

  scene_cleanup();

  switchOptions();

  radio_div.style.pointerEvents = 'none';
  button.value = "Please wait for process to finish";
  button.style.backgroundColor = 'aliceblue';

  if(options['vis_choice'] == 'gaussians'){
    fetch_gaussians();
  } else if(options['vis_choice'] == 'images'){
    fetch_image(0);
  } else if(options['vis_choice'] == 'video'){
    fetch_video();
  } else{
    console.log('An error occurred');
  }

  radio_div.style.pointerEvents = 'auto';
  button.value = 'Show Visualization';
  button.style.backgroundColor = '#85c1e9';

});

const prevButton = document.querySelector("#prev");
prevButton.addEventListener("click", () =>{
  prevImage();
});

const nextButton = document.querySelector("#next");
nextButton.addEventListener("click", () =>{
  nextImage();
})

function prevImage(){
  currIndex = currIndex - 1;
  fetch_image(currIndex);
}

function nextImage(){
  currIndex = currIndex + 1;
  fetch_image(currIndex);
}

/////////////////////////////////
//////// RENDERING FUNCTIONALITY
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
renderer.setSize( window.outerWidth, window.outerHeight );

const controls = new OrbitControls( camera, renderer.domElement );

function add_gaussian_to_scene(sample_json){

  const color = new THREE.Color(0, 255 * sample_json.opacity, 0);
  var material = new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: sample_json.opacity });

  const ellipsoidGeometry = new THREE.SphereGeometry(1, 32, 32);
  const ellipsoidMesh = new THREE.Mesh(ellipsoidGeometry, material);

  const offset = new THREE.Vector3(sample_json.avg_pos[0], sample_json.avg_pos[1], sample_json.avg_pos[2]);

  ellipsoidMesh.position.set(
    sample_json.position[0],
    sample_json.position[1],
    sample_json.position[2]
  );

  ellipsoidMesh.position.sub(offset);

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

function hide_scene(){
  scene_cleanup();
  renderer.domElement.remove();
}

function show_scene(){
  renderer.setAnimationLoop( animate );
  document.body.appendChild( renderer.domElement );
}

function animate() {

  // camera.lookAt(position[0], position[1], position[2]);

  controls.update();

  renderer.render( scene, camera );

}
