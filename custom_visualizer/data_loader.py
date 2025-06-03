import torch

def load_from_torch_file(path):
    data = torch.load(path)

    print(len(data))
    print(data[0].keys())

if __name__ == "__main__":
    path = '/home/omilchi/mvsplat_visualizer/datasets/re10k/test/000000.torch'

    load_from_torch_file(path)