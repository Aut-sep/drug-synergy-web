import random
import torch.nn.functional as F
import torch.nn as nn
from models.dualsyn import DualSyn
from utils_test import *
from sklearn.metrics import roc_curve, confusion_matrix
from sklearn.metrics import cohen_kappa_score, accuracy_score, roc_auc_score, precision_score, recall_score, \
    balanced_accuracy_score
from sklearn import metrics
from creat_data_DC import creat_data
import pandas as pd
import datetime
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument(
    '--result-name',
    default='DualSyn_transductive',
    help='Result folder and file prefix for this run.',
)
parser.add_argument(
    '--save-models',
    dest='save_models',
    action='store_true',
    help='Save best/final model checkpoints.',
)
parser.add_argument(
    '--no-save-models',
    dest='save_models',
    action='store_false',
    help='Do not save model checkpoints; only keep metrics files.',
)
parser.add_argument('--epochs', type=int, default=None, help='Override training epochs.')
parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto', help='Training device.')
parser.set_defaults(save_models=True)
args = parser.parse_args()

result_name = args.result_name
SAVE_MODELS = args.save_models

modeling = DualSyn

# training function at each epoch
def train(model, device, drug1_loader_train, drug2_loader_train, optimizer, epoch):
    print("===============")
    print('Training on {} samples...'.format(len(drug1_loader_train.dataset)))
    model.train()
    total_preds = torch.Tensor()
    total_labels = torch.Tensor()
    total_prelabels = torch.Tensor()

    zipped = zip(drug1_loader_train, drug2_loader_train)
    enumerate_data = enumerate(zipped)
    for batch_idx, data in enumerate_data:  
        data1 = data[0]
        data2 = data[1]
        data1 = data1.to(device)
        data2 = data2.to(device)
        y = data[0].y.view(-1, 1).float().to(device)
        y = y.squeeze(1)
        optimizer.zero_grad()
        output = model(data1, data2)
        loss = loss_fn(output, y)
        # print('loss', loss)
        loss.backward()
        optimizer.step()
        if batch_idx % LOG_INTERVAL == 0:
            print('Train epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(epoch,
                                                                           batch_idx * len(data1.x),
                                                                           len(drug1_loader_train.dataset),
                                                                           100. * batch_idx / len(drug1_loader_train),
                                                                           loss.item()))
        ys = output.to('cpu').data.numpy()
        predicted_labels = list(map(lambda x: int(x>0.5), ys))
        predicted_scores = list(map(lambda x: x, ys))
        total_preds = torch.cat((total_preds, torch.Tensor(predicted_scores)), 0)
        total_prelabels = torch.cat((total_prelabels, torch.Tensor(predicted_labels)), 0)
        total_labels = torch.cat((total_labels, data1.y.view(-1, 1).cpu()), 0)
    return total_labels.numpy().flatten(), total_preds.numpy().flatten(), total_prelabels.numpy().flatten()


def predicting(model, device, drug1_loader_test, drug2_loader_test):
    model.eval()
    total_preds = torch.Tensor()
    total_labels = torch.Tensor()
    total_prelabels = torch.Tensor()
    print('Make prediction for {} samples...'.format(len(drug1_loader_test.dataset)))
    with torch.no_grad():
        for data in zip(drug1_loader_test, drug2_loader_test):
            data1 = data[0]
            data2 = data[1]
            data1 = data1.to(device)
            data2 = data2.to(device)
            output = model(data1, data2)
            ys = output.to('cpu').data.numpy()
            predicted_labels = list(map(lambda x: int(x>0.5), ys))
            predicted_scores = list(map(lambda x: x, ys))
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


# CPU or GPU

if args.device == 'cpu':
    device = torch.device('cpu')
    print('The code uses CPU!!!')
elif args.device == 'cuda':
    device = torch.device('cuda:0')
    print('The code uses GPU...')
elif torch.cuda.is_available():
    device = torch.device('cuda:0')
    print('The code uses GPU...')
else:
    device = torch.device('cpu')
    print('The code uses CPU!!!')


TRAIN_BATCH_SIZE = 1024
TEST_BATCH_SIZE = 1024
LR = 0.0005
LOG_INTERVAL = 20
NUM_EPOCHS = 400
if args.epochs is not None:
    NUM_EPOCHS = args.epochs

print('Learning rate: ', LR)
print('Epochs: ', NUM_EPOCHS)

cellfile = 'data/cell_features_954.csv'  
drug_smiles_file = 'data/smiles.csv'  

# ── 指定你的五折文件路径 ──────────────────────────────────────
fold_train_files = [f'data/fold{i}/train.csv' for i in range(5)]
fold_val_files   = [f'data/fold{i}/test.csv'   for i in range(5)]
# ─────────────────────────────────────────────────────────────

folder_path = './result/' + result_name
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

save_model_dir = './save_model'
if SAVE_MODELS and not os.path.exists(save_model_dir):
    os.makedirs(save_model_dir)


for i in range(5):
    print(f'\n========== Fold {i} ==========')

    # 加载训练集
    print('开始处理源文件....')
    train_drug1, train_drug2, train_cell, train_label, smile_graph, cell_features = \
        creat_data(fold_train_files[i], drug_smiles_file, cellfile)
    print('从源文件提取特征成功！')

    print('载入数据...')
    drug1_data_train = TestbedDataset(
        dataset=f'fold{i}_train_drug1',
        xd=train_drug1, xt=train_cell, y=train_label,
        smile_graph=smile_graph, xt_featrue=cell_features)
    drug2_data_train = TestbedDataset(
        dataset=f'fold{i}_train_drug2',
        xd=train_drug2, xt=train_cell, y=train_label,
        smile_graph=smile_graph, xt_featrue=cell_features)
    print('载入数据完成！')

    # 加载验证集
    print('开始处理源文件....')
    val_drug1, val_drug2, val_cell, val_label, smile_graph, cell_features = \
        creat_data(fold_val_files[i], drug_smiles_file, cellfile)
    print('从源文件提取特征成功！')

    print('载入数据...')
    drug1_data_val = TestbedDataset(
        dataset=f'fold{i}_val_drug1',
        xd=val_drug1, xt=val_cell, y=val_label,
        smile_graph=smile_graph, xt_featrue=cell_features)
    drug2_data_val = TestbedDataset(
        dataset=f'fold{i}_val_drug2',
        xd=val_drug2, xt=val_cell, y=val_label,
        smile_graph=smile_graph, xt_featrue=cell_features)
    print('载入数据完成！')

    drug1_loader_train = DataLoader(drug1_data_train, batch_size=TRAIN_BATCH_SIZE, shuffle=None)
    drug2_loader_train = DataLoader(drug2_data_train, batch_size=TRAIN_BATCH_SIZE, shuffle=None)
    drug1_loader_test  = DataLoader(drug1_data_val,   batch_size=TEST_BATCH_SIZE,  shuffle=None)
    drug2_loader_test  = DataLoader(drug2_data_val,   batch_size=TEST_BATCH_SIZE,  shuffle=None)

    model = modeling().to(device)
    #loss_fn = nn.CrossEntropyLoss()
    loss_fn = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    now = datetime.datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    file_AUCs = folder_path + '/' + result_name + '_' + str(i) + '--AUCs--fold' + str(i) + '_' + time_str + '.txt'
    AUCs = ('Epoch\tAUC_dev\tPR_AUC\tACC\tBACC\tPREC\tTPR\tKAPPA\tRECALL')
    with open(file_AUCs, 'w') as f:
        f.write(AUCs + '\n')

    best_auc = 0
    best_epoch = -1
    best_model_path = os.path.join(save_model_dir, f'{result_name}_{i}_best_auc.pt')
    final_model_path = os.path.join(save_model_dir, f'{result_name}_{i}_final_epoch={NUM_EPOCHS}.pt')
    for epoch in range(NUM_EPOCHS):
        train_T, train_S, train_Y = train(model, device, drug1_loader_train, drug2_loader_train, optimizer, epoch + 1)
        T, S, Y = predicting(model, device, drug1_loader_test, drug2_loader_test)
        # T is correct label
        # S is predict score
        # Y is predict label

        # compute preformence
        AUC = roc_auc_score(T, S)
        precision, recall, threshold = metrics.precision_recall_curve(T, S)
        PR_AUC = metrics.auc(recall, precision)
        BACC = balanced_accuracy_score(T, Y)
        tn, fp, fn, tp = confusion_matrix(T, Y).ravel()
        TPR = tp / (tp + fn)
        PREC = precision_score(T, Y)
        ACC = accuracy_score(T, Y)
        KAPPA = cohen_kappa_score(T, Y)
        recall = recall_score(T, Y)

        train_AUC = roc_auc_score(train_T, train_S)
        train_precision, train_recall, train_threshold = metrics.precision_recall_curve(train_T, train_S)
        train_PR_AUC = metrics.auc(train_recall, train_precision)
        train_ACC = accuracy_score(train_T, train_Y)
        
        print("Train: AUC={}, PR_AUC={}, ACC={}".format(train_AUC, train_PR_AUC, train_ACC))
        print("Test: AUC={}, PR_AUC={}, ACC={}".format(AUC, PR_AUC, ACC))

        # save data
        if best_auc < AUC:
            best_auc = AUC
            best_epoch = epoch
            if SAVE_MODELS:
                torch.save(model.state_dict(), best_model_path)

            AUCs = [epoch, AUC, PR_AUC, ACC, BACC, PREC, TPR, KAPPA, recall]
            save_AUCs(AUCs, file_AUCs)
        
        print('best_auc', best_auc)  
    save_AUCs("best_auc:" + str(best_auc), file_AUCs)
    save_AUCs("best_epoch:" + str(best_epoch), file_AUCs)
    if SAVE_MODELS:
        save_AUCs("best_model_path:" + best_model_path, file_AUCs)
        torch.save(model.state_dict(), final_model_path)
    else:
        save_AUCs("best_model_path: not_saved", file_AUCs)
