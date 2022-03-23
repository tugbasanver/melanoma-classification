import pandas as pd
import numpy as np
import glob
from sklearn.metrics import roc_auc_score, roc_curve, plot_roc_curve, confusion_matrix
import warnings

# Remove this to see the warning.
warnings.filterwarnings("ignore")


def pretty_per_num(num):
    return round(num * 100, 2)


def calc_metrics(pred, target, model_nm):
    #target = np.array(target).astype(np.int8).tolist()
    auc_score = roc_auc_score(target, pred)
    fpr, tpr, thr = roc_curve(target, pred)
    gmeans = np.sqrt(tpr * (1 - fpr))
    npv = []
    for i in range(len(thr)):
        temp_thr = thr[i]
        pred_thr = [True if p > temp_thr else False for p in pred]
        tn, fp, fn, tp = confusion_matrix(target, pred_thr).ravel()
        npv.append(tn / (tn + fn + 1e-12))
    npv = np.array(npv)
    # Here whatever we want to maximize, just write that. i.e. np.argmax(npv) will maximize npv, and np.argmax(gmeans) will maximize gmeans.
    ix = np.argmax(gmeans)
    bestg = gmeans[ix]
    bestthr = thr[ix]
    bestnpv = npv[ix]
    val = "Best Threshold=%f, G-Mean=%.3f, NPV=%.3f" % (
        bestthr,
        pretty_per_num(bestg),
        pretty_per_num(bestnpv),
    )
    pred_thr = [True if p > bestthr else False for p in pred]
    tn, fp, fn, tp = confusion_matrix(target, pred_thr).ravel()
    sensitivity = tp / (tp + fn + 1e-12)   
    specificity = tn / (tn + fp + 1e-12)
    #import pdb; pdb.set_trace()
    print(
        "\nFollowing are the metrics for " + model_nm + ": AUC_Score:",
        pretty_per_num(auc_score),
        val,
        "Sensitivity:",
        pretty_per_num(sensitivity),
        "Specificity:",
        pretty_per_num(specificity),
    )


def calculate_metric_ensemble(path):
    files = glob.glob(path)

    targets = {}
    preds = {}
    samessies = {}
    for f in files:
        data = pd.read_csv(f)
        targ = data["target"] == data["mel_index"].iloc[0]
        targ = list(targ.values)
        nm = f.split("/")[-1].replace("melData_", "").replace("_.csv", "")
        targets[nm] = targ
        if tuple(targ) in samessies.keys():
            samessies[tuple(targ)].append(nm)
        else:
            samessies[tuple(targ)] = [nm]
        preds[nm] = list(data["pred"].values)
        calc_metrics(
            list(data["pred"]), list((data["target"] == data["mel_index"].iloc[0])), nm
        )


def main():
    calculate_metric_ensemble("./results/*.csv")


if __name__ == "__main__":
    main()

