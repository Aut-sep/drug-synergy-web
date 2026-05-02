import argparse
import os
import random
import warnings

import pandas as pd
import torch.nn as nn
import torch.nn.functional as F
import torch_geometric.deprecation
from models.MFSynDCP import MFSynDCP
from sklearn import metrics
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    cohen_kappa_score,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)
from utils_test import *


warnings.filterwarnings("ignore", category=UserWarning, module="torch_geometric.deprecation")


def train(model, device, drug1_loader_train, drug2_loader_train, optimizer, epoch):
    print("Training on {} samples...".format(len(drug1_loader_train.dataset)))
    model.train()
    for batch_idx, data in enumerate(zip(drug1_loader_train, drug2_loader_train)):
        data1 = data[0]
        data2 = data[1]
        data1 = data1.to(device)
        data2 = data2.to(device)
        y = data[0].y.view(-1, 1).long().to(device)
        y = y.squeeze(1)
        optimizer.zero_grad()
        output = model(data1, data2)
        loss = loss_fn(output, y)
        loss.backward()
        optimizer.step()
        if batch_idx % LOG_INTERVAL == 0:
            processed_samples = batch_idx * TRAIN_BATCH_SIZE
            print(
                "Train epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}".format(
                    epoch,
                    processed_samples,
                    len(drug1_loader_train.dataset),
                    100.0 * processed_samples / len(drug1_loader_train.dataset),
                    loss.item(),
                )
            )


def predicting(model, device, drug1_loader_test, drug2_loader_test):
    model.eval()
    total_preds = torch.Tensor()
    total_labels = torch.Tensor()
    total_prelabels = torch.Tensor()
    print("Make prediction for {} samples...".format(len(drug1_loader_test.dataset)))
    with torch.no_grad():
        for data in zip(drug1_loader_test, drug2_loader_test):
            data1 = data[0]
            data2 = data[1]
            data1 = data1.to(device)
            data2 = data2.to(device)
            output = model(data1, data2)
            ys = F.softmax(output, 1).to("cpu").data.numpy()
            predicted_labels = list(map(lambda x: np.argmax(x), ys))
            predicted_scores = list(map(lambda x: x[1], ys))
            total_preds = torch.cat((total_preds, torch.Tensor(predicted_scores)), 0)
            total_prelabels = torch.cat((total_prelabels, torch.Tensor(predicted_labels)), 0)
            total_labels = torch.cat((total_labels, data1.y.view(-1, 1).cpu()), 0)
    return total_labels.numpy().flatten(), total_preds.numpy().flatten(), total_prelabels.numpy().flatten()


def shuffle_dataset(dataset, seed):
    np.random.seed(seed)
    np.random.shuffle(dataset)
    return dataset


def split_dataset(dataset, ratio):
    n = int(len(dataset) * ratio)
    dataset_1, dataset_2 = dataset[:n], dataset[n:]
    return dataset_1, dataset_2


modeling = MFSynDCP

parser = argparse.ArgumentParser()
parser.add_argument(
    "--result-prefix",
    default="MFSynDCP",
    help="Prefix used for result and model filenames.",
)
parser.add_argument(
    "--result-tag",
    default="labels",
    help="Suffix tag used in metric filenames.",
)
parser.add_argument(
    "--save-models",
    dest="save_models",
    action="store_true",
    help="Save best model checkpoints.",
)
parser.add_argument(
    "--no-save-models",
    dest="save_models",
    action="store_false",
    help="Do not save model checkpoints; only keep metric files.",
)
parser.add_argument("--epochs", type=int, default=None, help="Override training epochs.")
parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto", help="Training device.")
parser.set_defaults(save_models=True)
args = parser.parse_args()

TRAIN_BATCH_SIZE = 128
TEST_BATCH_SIZE = 256
LR = 0.0001
LOG_INTERVAL = 20
NUM_EPOCHS = 500
if args.epochs is not None:
    NUM_EPOCHS = args.epochs

print("Learning rate: ", LR)
print("Epochs: ", NUM_EPOCHS)
datafile = args.result_tag
result_prefix = args.result_prefix
SAVE_MODELS = args.save_models

os.environ["CUDA_VISIBLE_DEVICES"] = "1"

if args.device == "cpu":
    device = torch.device("cpu")
    print("The code uses CPU!!!")
elif args.device == "cuda":
    device = torch.device("cuda")
    print("The code uses GPU...")
elif torch.cuda.is_available():
    device = torch.device("cuda")
    print("The code uses GPU...")
else:
    device = torch.device("cpu")
    print("The code uses CPU!!!")


for i in range(5):
    drug1_data_train = TestbedDataset(root="data", dataset=f"fold{i}_train_drug1")
    drug1_data_test = TestbedDataset(root="data", dataset=f"fold{i}_test_drug1")
    drug2_data_train = TestbedDataset(root="data", dataset=f"fold{i}_train_drug2")
    drug2_data_test = TestbedDataset(root="data", dataset=f"fold{i}_test_drug2")

    drug1_loader_train = DataLoader(drug1_data_train, batch_size=TRAIN_BATCH_SIZE, shuffle=True)
    drug1_loader_test = DataLoader(drug1_data_test, batch_size=TRAIN_BATCH_SIZE, shuffle=False)
    drug2_loader_train = DataLoader(drug2_data_train, batch_size=TRAIN_BATCH_SIZE, shuffle=True)
    drug2_loader_test = DataLoader(drug2_data_test, batch_size=TRAIN_BATCH_SIZE, shuffle=False)

    model = modeling().to(device)
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    model_file_name = f"result/{result_prefix}_fold{i}.model"
    result_file_name = f"result/{result_prefix}_fold{i}_result_{datafile}.csv"
    file_AUCs = f"result/{result_prefix}_fold{i}_AUCs_{datafile}.txt"
    AUCs = "Epoch\tAUC_dev\tPR_AUC\tACC\tBACC\tPREC\tTPR\tKAPPA\tRECALL"
    with open(file_AUCs, "w") as f:
        f.write(AUCs + "\n")

    best_auc = 0
    for epoch in range(NUM_EPOCHS):
        train(model, device, drug1_loader_train, drug2_loader_train, optimizer, epoch + 1)
        T, S, Y = predicting(model, device, drug1_loader_test, drug2_loader_test)

        AUC = roc_auc_score(T, S)
        precision, recall, threshold = metrics.precision_recall_curve(T, S)
        PR_AUC = metrics.auc(recall, precision)
        BACC = balanced_accuracy_score(T, Y)
        tn, fp, fn, tp = confusion_matrix(T, Y).ravel()
        TPR = tp / (tp + fn)
        PREC = precision_score(T, Y, zero_division=1)
        ACC = accuracy_score(T, Y)
        KAPPA = cohen_kappa_score(T, Y)
        recall = recall_score(T, Y)

        AUCs = [epoch, AUC, PR_AUC, ACC, BACC, PREC, TPR, KAPPA, recall]
        save_AUCs(AUCs, file_AUCs)

        if best_auc < AUC:
            best_auc = AUC
            print(f"Fold {i}, Epoch {epoch}, Best AUC: {best_auc:.4f}")
            if SAVE_MODELS:
                torch.save(model.state_dict(), model_file_name)
