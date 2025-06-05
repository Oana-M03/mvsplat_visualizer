import * as THREE from 'three';

const sample_json = {
  "position": [-0.024850094690918922, -0.010145621374249458, -0.13689498603343964], 
  "opacity": 0.48494166135787964, 
  "scales": [0.0005547910695895553, 0.0005728864343836904, 0.000551257049664855], 
  "rotation": [0.9204495101593337, -0.6861311735362289, 1.0780237193784532]
}

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.001, 1000);

const ellipsoidPosition = sample_json.position;

camera.position.set(
  ellipsoidPosition[0] + 0.01,
  ellipsoidPosition[1],
  ellipsoidPosition[2]
);
// camera.updateProjectionMatrix();

camera.lookAt(
  ellipsoidPosition[0],
  ellipsoidPosition[1],
  ellipsoidPosition[2]
);
// camera.updateProjectionMatrix();

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

add_gaussian_to_scene(sample_json);

function animate() {

  renderer.render( scene, camera );

}
