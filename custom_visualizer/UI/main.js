import * as THREE from 'three';

const button = document.querySelector(".render-button");

button.addEventListener("click", () => {

  fetch('http://localhost:5000/data', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: "Send Gaussians", value: 42 })
  })
  .then(response => response.json())
  .then(data => {
    data.forEach(gaussian => {
      add_gaussian_to_scene(gaussian);
    })
    // console.log('Response from backend:', data);
  })
  .catch(error => console.error('Error:', error));

});

// RENDER GAUSSIANS ON SCREEN
const position = [0, 0, 0];

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.001, 1000);

const ellipsoidPosition = position;

camera.position.set(
  ellipsoidPosition[0] + 0.5,
  ellipsoidPosition[1],
  ellipsoidPosition[2] + 0.5
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
