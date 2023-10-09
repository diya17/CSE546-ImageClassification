#!/usr/bin/env python3
import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import numpy as np
import json
import sys
import time
import os

class CustomImageDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.file_list = os.listdir(root_dir)

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, idx):
        img_name = self.file_list[idx]
        image = Image.open(os.path.join(self.root_dir, self.file_list[idx]))

        if self.transform:
            image = self.transform(image)
        
        return image, img_name


class ImageClassifier():
    def __init__(self, rootDirectory):
        self.dataDirectory = os.path.join(rootDirectory, "user-input")
        self.transform = transforms.Compose([transforms.ToTensor()])
        self.model = models.resnet18(pretrained=True)
        self.jsonPath = os.path.join(rootDirectory, "imagenet-labels.json")

    def modelInference(self, batch_size):
        start_time = time.time()
        dataset = CustomImageDataset(self.dataDirectory, transform=self.transform)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        self.model.eval()

        save_dict = dict()
        for batch in dataloader:
            images, filenames = batch
            outputs = self.model(images)
            _, predicted = torch.max(outputs.data, 1)
            with open(self.jsonPath) as f:
                labels = json.load(f)
            for idx, pred in enumerate(predicted):
                result = labels[np.array(pred)]
                imgName = filenames[idx]
                save_dict[imgName]=result

        end_time = time.time()
        inference_time = end_time - start_time
        print(save_dict)
        print(f"Inference time: {inference_time} seconds")
        return save_dict