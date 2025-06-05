import * as THREE from 'three';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );

const renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
renderer.setAnimationLoop( animate );
document.body.appendChild( renderer.domElement );

const ellipsoidGeometry = new THREE.SphereGeometry(0.5, 32, 16);
ellipsoidGeometry.rotateZ(Math.PI/2);
ellipsoidGeometry.scale(2, 1, 1);

const material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );

const ellipsoidMesh = new THREE.Mesh(ellipsoidGeometry, material);

scene.add(ellipsoidMesh);

camera.position.z = 5;

function animate() {

  renderer.render( scene, camera );

}
