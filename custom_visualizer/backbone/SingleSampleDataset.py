from torch.utils.data import Dataset

class SingleSampleDataset(Dataset):
    def __init__(self, dataset: Dataset, index: int):
        if index >= len(dataset):
            raise IndexError(f"Index {index} is out of range for dataset of size {len(dataset)}")

        iterator = iter(dataset)
        for _ in range(index):
            next(iterator)
        self.instance = next(iterator)

    def __len__(self):
        return 1

    def __getitem__(self, idx):

        if idx > 0:
            raise IndexError(f"Index {idx} is out of range for dataset of size 1")

        return self.instance