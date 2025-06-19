# MVSplat Visualizer
## By Elena-Oana Milchi

This repository contains an app that visualizes the MVSplat pipeline, namely the final video render and the Gaussians resulting from the encoder.

## Setup instructions

The necessary datasets can be acquired at [this link](https://drive.google.com/drive/folders/1joiezNCyQK2BvWMnfwHJpm2V77c7iYGe). We recommend downloading the RE10k dataset and unzip it into a a newly created datasets folder in the project root directory.

The necessary models and ablations can be acquired at [this link](https://drive.google.com/drive/folders/14_E_5R6ojOWnLSrSVLVEMHnTiKsfddjU). We recommend downloading ``re10k.ckpt`` as well as the ``ablations`` folder, and copying both to the ``/checkpoints`` folder.

### Backend
Run the following instructions to set up the conda environment.

~~~ 
conda create -n mvsplat python=3.10
conda activate mvsplat
pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118
pip install -r final_requirements.txt 
~~~

To start up the backend (with the re10k dataset), run the following instructions from the root folder:

- for linux machines: ensure that GLIBCXX_3.4.29 can be found
~~~
export LD_LIBRARY_PATH=$(conda info --base)/envs/mvsplat/lib:$LD_LIBRARY_PATH
~~~

- run the backend
~~~
python -m custom_visualizer.backbone.main +experiment=re10k checkpointing.load=checkpoints/re10k.ckpt mode=test dataset/view_sampler=evaluation
~~~

### Frontend

**Note:** you will need to have Node and npm installed on your computer.

~~~
cd mvsplat_visualizer/custom_visualizer/UI
npm install three
~~~

To run the frontend simply run the following commands:

~~~
cd mvsplat_visualizer/custom_visualizer/UI
npx vite
~~~

## External resources

- MVSplat [1] - original Gaussian Splatting algorithm to be visualized. This repository is a fork of the original MVSplat repository.
  - Checkpoints of the model and the ablations were obtained from the original repository.
- Differential Gaussian Rasterizer [2] - employed by MVSplat to render the Gaussians into the final video result.
- RealEstate 10k dataset [3] - test set employed for visualization samples.


## References

[1] Chen, Y., Xu, H., Zheng, C., Zhuang, B., Pollefeys, M., Geiger, A., Cham, T.-J., & Cai, J. (2024). MVSplat: Efficient 3D Gaussian Splatting from Sparse Multi-View Images. ArXiv Preprint ArXiv:2403.14627.

[2] Kerbl, B., Kopanas, G., Leimkühler, T., & Drettakis, G. (2023). 3D Gaussian Splatting for Real-Time Radiance Field Rendering. ACM Transactions on Graphics, 42(4). https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/

[3] Tinghui Zhou, Richard Tucker, John Flynn, Graham Fyffe, and Noah Snavely. Stereo magnification: Learning view synthesis using multiplane images. arXiv preprint arXiv:1805.09817, 2018.