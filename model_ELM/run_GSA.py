import os
from concurrent.futures import ThreadPoolExecutor

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from SALib.analyze import pawn, sobol
from SALib.sample import saltelli

matplotlib.use("Agg")

try:
    from model_ELM.surrogate_NN_Forcing import (
        DEFAULT_SPINUP_VARS,
        _spinup_state,
        build_forcing_inference_inputs,
        load_surrogate_forcing_artifacts,
    )
except ImportError:  # pragma: no cover
    from surrogate_NN_Forcing import (  # type: ignore
        DEFAULT_SPINUP_VARS,
        _spinup_state,
        build_forcing_inference_inputs,
        load_surrogate_forcing_artifacts,
    )


def _normalize_var_list(myvars):
    if isinstance(myvars, str):
        return [v.strip() for v in myvars.split(",") if v.strip() and v.strip() != "taxis"]
    return [str(v).strip() for v in myvars if str(v).strip() and str(v).strip() != "taxis"]


def _default_output_dir(case):
    return os.path.join(".", "UQ_output", case.casename, "GSA")


def _resolve_output_dir(case, output_dir=None):
    out = _default_output_dir(case) if output_dir is None else str(output_dir)
    os.makedirs(out, exist_ok=True)
    return out


def _base_param_labels(case):
    labels = []
    for i, p in enumerate(case.ensemble_parms):
        if hasattr(case, "ensemble_pfts") and len(case.ensemble_pfts) > i:
            labels.append(f"{p}{case.ensemble_pfts[i]}")
        else:
            labels.append(str(p))
    return labels


def _base_param_bounds(case):
    pbounds = np.zeros((int(case.nparms_ensemble), 2), float)
    for p in range(int(case.nparms_ensemble)):
        pbounds[p, 0] = float(case.ensemble_pmin[p])
        pbounds[p, 1] = float(case.ensemble_pmax[p])
    return pbounds


def _collect_spinup_matrix(case, spinup_vars):
    nsamples = int(np.asarray(case.samples).shape[1])
    spinup = np.zeros((nsamples, len(spinup_vars)), dtype=np.float64)
    for ens_num in range(1, nsamples + 1):
        spinup[ens_num - 1, :] = _spinup_state(case, ens_num, spinup_vars)
    return spinup


def _parallel_map(work, indices, n_jobs):
    if int(n_jobs) <= 1:
        return [work(i) for i in indices]
    with ThreadPoolExecutor(max_workers=int(n_jobs)) as exe:
        return list(exe.map(work, indices))


def _run_sobol_timeseries(problem, y2d, n_jobs=1):
    ntime = y2d.shape[1]

    def _worker(i):
        si = sobol.analyze(problem, y2d[:, i], print_to_console=False)
        return np.asarray(si["S1"], dtype=np.float64), np.asarray(si["ST"], dtype=np.float64)

    rows = _parallel_map(_worker, range(ntime), n_jobs)
    s1 = np.column_stack([r[0] for r in rows])
    st = np.column_stack([r[1] for r in rows])
    return s1, st


def _run_pawn_timeseries(problem, x, y2d, n_jobs=1, pawn_s=10):
    ntime = y2d.shape[1]

    def _worker(i):
        out = pawn.analyze(problem, x, y2d[:, i], S=pawn_s, print_to_console=False)
        return np.asarray(out["median"], dtype=np.float64)

    rows = _parallel_map(_worker, range(ntime), n_jobs)
    return np.column_stack(rows)


def _plot_heatmap(matrix, row_labels, title, fname):
    arr = np.asarray(matrix, dtype=np.float64)
    fig_h = max(4.0, min(12.0, 0.35 * arr.shape[0] + 2.0))
    fig_w = max(10.0, min(18.0, 0.004 * arr.shape[1] + 10.0))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    im = ax.imshow(arr, aspect="auto", origin="lower", interpolation="nearest")
    ax.set_title(title)
    ax.set_xlabel("Time index")
    ax.set_ylabel("Input")
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_yticklabels(row_labels)
    fig.colorbar(im, ax=ax, label="Sensitivity")
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight")
    plt.close(fig)


def GSA(self, myvars, n_saltelli=8192, n_jobs=1, output_dir=None):
    pbounds = _base_param_bounds(self)
    problem = {"num_vars": int(self.nparms_ensemble), "names": list(self.ensemble_parms), "bounds": pbounds}
    psamples = saltelli.sample(problem, int(n_saltelli))
    myvars_list = _normalize_var_list(myvars)
    surrogate_output = self.run_surrogate(psamples, myvars_list)
    self.sens_main = {}
    self.sens_tot = {}
    self.sens_main_names = _base_param_labels(self)

    for v in myvars_list:
        y2d = np.asarray(surrogate_output[v], dtype=np.float64)
        self.sens_main[v], self.sens_tot[v] = _run_sobol_timeseries(problem, y2d, n_jobs=n_jobs)

    if output_dir is not None:
        plot_GSA(self, myvars_list, output_dir=output_dir)


def GSA_given_data_pawn(
    self,
    myvars,
    include_spinup=False,
    spinup_vars=None,
    n_jobs=1,
    pawn_s=10,
    output_dir=None,
):
    myvars_list = _normalize_var_list(myvars)
    x = np.asarray(self.samples, dtype=np.float64).transpose()
    names = _base_param_labels(self)

    if include_spinup:
        spinup_names = list(DEFAULT_SPINUP_VARS if spinup_vars is None else spinup_vars)
        spinup = _collect_spinup_matrix(self, spinup_names)
        x = np.column_stack((x, spinup))
        names = names + [f"spinup_{v}" for v in spinup_names]

    bounds = np.column_stack((np.min(x, axis=0), np.max(x, axis=0)))
    problem = {"num_vars": int(x.shape[1]), "names": names, "bounds": bounds.tolist()}

    self.sens_pawn = {}
    self.sens_pawn_names = names
    for v in myvars_list:
        y2d = np.asarray(self.output[v], dtype=np.float64).transpose()
        if y2d.shape[0] != x.shape[0]:
            raise ValueError(
                f"Sample mismatch for {v}: X has {x.shape[0]} rows, output has {y2d.shape[0]} rows."
            )
        self.sens_pawn[v] = _run_pawn_timeseries(problem, x, y2d, n_jobs=n_jobs, pawn_s=int(pawn_s))

    plot_GSA_pawn(self, myvars_list, output_dir=output_dir)


def GSA_forcing_timeseries(
    self,
    myvars,
    n_saltelli=1024,
    spinup_vars=None,
    n_jobs=1,
    output_dir=None,
    artifact_path=None,
):
    if artifact_path is not None:
        load_surrogate_forcing_artifacts(self, artifact_path)
    if not hasattr(self, "forcing_surrogate_training"):
        raise AttributeError(
            "forcing_surrogate_training metadata not found. Train/load forcing surrogate first."
        )

    myvars_list = _normalize_var_list(myvars)
    spinup_names = list(DEFAULT_SPINUP_VARS if spinup_vars is None else spinup_vars)
    forcing_ctx = build_forcing_inference_inputs(self, self.forcing_surrogate_training, spinup_member=1)
    forcing_fixed = np.asarray(forcing_ctx["forcing_engineered"], dtype=np.float64)

    spinup_matrix = _collect_spinup_matrix(self, spinup_names)
    pbounds = _base_param_bounds(self)
    spinup_bounds = np.column_stack((np.min(spinup_matrix, axis=0), np.max(spinup_matrix, axis=0)))
    all_bounds = np.vstack((pbounds, spinup_bounds))
    all_names = _base_param_labels(self) + [f"spinup_{v}" for v in spinup_names]

    problem = {"num_vars": int(all_bounds.shape[0]), "names": all_names, "bounds": all_bounds.tolist()}
    print("GSA forcing problem is:")
    print(problem)
    print()
    
    samples = saltelli.sample(problem, int(n_saltelli))
    n_param = int(self.nparms_ensemble)
    n_eval = samples.shape[0]
    ntime = forcing_fixed.shape[0]

    pred = {v: np.zeros((n_eval, ntime), dtype=np.float64) for v in myvars_list}
    for i in range(n_eval):
        parm_i = samples[i, :n_param]
        spinup_i = samples[i, n_param:]
        out_i = self.run_surrogate_forcing(
            parm_i,
            myvars_list,
            forcing_engineered=forcing_fixed,
            spinup=spinup_i,
        )
        for v in myvars_list:
            pred[v][i, :] = np.asarray(out_i[v], dtype=np.float64).ravel()

    self.sens_forcing_main = {}
    self.sens_forcing_tot = {}
    self.sens_forcing_names = all_names
    for v in myvars_list:
        self.sens_forcing_main[v], self.sens_forcing_tot[v] = _run_sobol_timeseries(
            problem, pred[v], n_jobs=n_jobs
        )

    plot_GSA_forcing(self, myvars_list, output_dir=output_dir)


def plot_GSA(self, myvars, output_dir=None):
    outdir = _resolve_output_dir(self, output_dir)
    myvars_list = _normalize_var_list(myvars)
    names = list(getattr(self, "sens_main_names", _base_param_labels(self)))
    for v in myvars_list:
        if v not in self.sens_main:
            continue
        main = np.asarray(self.sens_main[v], dtype=np.float64)
        tot = np.asarray(self.sens_tot[v], dtype=np.float64)
        np.savez(os.path.join(outdir, f"sobol_{v}.npz"), S1=main, ST=tot, names=np.asarray(names, dtype=object))
        _plot_heatmap(main, names, f"Sobol S1 - {v}", os.path.join(outdir, f"sens_main_{v}.png"))
        _plot_heatmap(tot, names, f"Sobol ST - {v}", os.path.join(outdir, f"sens_tot_{v}.png"))


def plot_GSA_pawn(self, myvars, output_dir=None):
    outdir = _resolve_output_dir(self, output_dir)
    myvars_list = _normalize_var_list(myvars)
    names = list(getattr(self, "sens_pawn_names", _base_param_labels(self)))
    for v in myvars_list:
        if v not in self.sens_pawn:
            continue
        pawn_median = np.asarray(self.sens_pawn[v], dtype=np.float64)
        np.savez(
            os.path.join(outdir, f"pawn_{v}.npz"),
            median=pawn_median,
            names=np.asarray(names, dtype=object),
        )
        _plot_heatmap(
            pawn_median,
            names,
            f"PAWN median index - {v}",
            os.path.join(outdir, f"pawn_median_{v}.png"),
        )


def plot_GSA_forcing(self, myvars, output_dir=None):
    outdir = _resolve_output_dir(self, output_dir)
    myvars_list = _normalize_var_list(myvars)
    names = list(getattr(self, "sens_forcing_names", _base_param_labels(self)))
    for v in myvars_list:
        if v not in self.sens_forcing_main:
            continue
        main = np.asarray(self.sens_forcing_main[v], dtype=np.float64)
        tot = np.asarray(self.sens_forcing_tot[v], dtype=np.float64)
        np.savez(
            os.path.join(outdir, f"forcing_sobol_{v}.npz"),
            S1=main,
            ST=tot,
            names=np.asarray(names, dtype=object),
        )
        _plot_heatmap(
            main,
            names,
            f"Forcing surrogate Sobol S1 - {v}",
            os.path.join(outdir, f"forcing_sens_main_{v}.png"),
        )
        _plot_heatmap(
            tot,
            names,
            f"Forcing surrogate Sobol ST - {v}",
            os.path.join(outdir, f"forcing_sens_tot_{v}.png"),
        )
