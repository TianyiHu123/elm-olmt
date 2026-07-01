import os
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

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


SUPPORTED_AGG_METRICS = ("mean", "accumulated", "std")
SUPPORTED_EXECUTORS = ("serial", "thread", "process")

try:
    import resource
except ImportError:  # pragma: no cover
    resource = None


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
            labels.append(f"{p}_pft{case.ensemble_pfts[i]}")
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


def _normalize_metric_list(metrics):
    if metrics is None:
        requested = list(SUPPORTED_AGG_METRICS)
    elif isinstance(metrics, str):
        requested = [m.strip().lower() for m in metrics.split(",") if m.strip()]
    else:
        requested = [str(m).strip().lower() for m in metrics if str(m).strip()]

    unknown = sorted(set(requested).difference(SUPPORTED_AGG_METRICS))
    if unknown:
        known = ", ".join(SUPPORTED_AGG_METRICS)
        raise ValueError(f"Unknown metrics {unknown}. Supported metrics are: {known}.")

    selected = []
    requested_set = set(requested)
    for metric in SUPPORTED_AGG_METRICS:
        if metric in requested_set:
            selected.append(metric)
    if not selected:
        known = ", ".join(SUPPORTED_AGG_METRICS)
        raise ValueError(f"No valid metrics requested. Supported metrics are: {known}.")
    return selected


def _normalize_executor_mode(executor):
    mode = "thread" if executor is None else str(executor).strip().lower()
    if mode not in SUPPORTED_EXECUTORS:
        known = ", ".join(SUPPORTED_EXECUTORS)
        raise ValueError(f"Unknown executor mode '{executor}'. Supported modes are: {known}.")
    return mode


def _analysis_executor_mode(executor, context):
    mode = _normalize_executor_mode(executor)
    if mode == "process":
        print(f"[GSA] {context}: process mode not supported for this path; using thread.")
        return "thread"
    return mode


def _resolve_worker_count(n_jobs, n_items):
    n_items_int = int(n_items)
    if n_items_int <= 0:
        return 1
    requested = max(1, int(n_jobs))
    cpu = os.cpu_count() or 1
    return max(1, min(requested, cpu, n_items_int))


def _resolve_chunk_size(chunk_size, total_items, workers):
    total = max(1, int(total_items))
    if chunk_size is None:
        return max(1, min(256, int(np.ceil(total / max(1, int(workers))))))
    return max(1, int(chunk_size))


def _current_rss_gb():
    if resource is None:
        return None
    usage = resource.getrusage(resource.RUSAGE_SELF)
    rss = float(usage.ru_maxrss)
    if os.name == "posix":
        rss /= 1024.0 * 1024.0
    else:  # pragma: no cover
        rss /= 1024.0 * 1024.0 * 1024.0
    return rss


def _log_checkpoint(label, start_time):
    elapsed = time.perf_counter() - float(start_time)
    rss_gb = _current_rss_gb()
    if rss_gb is None:
        print(f"[GSA] {label}: elapsed={elapsed:.2f}s")
    else:
        print(f"[GSA] {label}: elapsed={elapsed:.2f}s rss_max={rss_gb:.2f}GB")


def _aggregate_outputs(y2d, metrics):
    y2d_arr = np.asarray(y2d, dtype=np.float64)
    if y2d_arr.ndim != 2:
        raise ValueError(f"Expected 2D response matrix, got shape {y2d_arr.shape}.")

    out = {}
    for metric in metrics:
        if metric == "mean":
            out[metric] = np.nanmean(y2d_arr, axis=1, keepdims=True)
        elif metric == "accumulated":
            out[metric] = np.nansum(y2d_arr, axis=1, keepdims=True)
        elif metric == "std":
            out[metric] = np.nanstd(y2d_arr, axis=1, keepdims=True)
    return out


def _parallel_map(work, indices, n_jobs, executor="thread"):
    mode = _normalize_executor_mode(executor)
    if mode == "serial" or int(n_jobs) <= 1:
        return [work(i) for i in indices]
    max_workers = _resolve_worker_count(n_jobs, len(indices))
    executor_cls = ProcessPoolExecutor if mode == "process" else ThreadPoolExecutor
    with executor_cls(max_workers=max_workers) as exe:
        return list(exe.map(work, indices))


def _run_sobol_timeseries(problem, y2d, n_jobs=1, executor="thread"):
    ntime = y2d.shape[1]
    mode = _analysis_executor_mode(executor, "_run_sobol_timeseries")

    def _worker(i):
        si = sobol.analyze(problem, y2d[:, i], print_to_console=False)
        return np.asarray(si["S1"], dtype=np.float64), np.asarray(si["ST"], dtype=np.float64)

    rows = _parallel_map(_worker, range(ntime), n_jobs, executor=mode)
    s1 = np.column_stack([r[0] for r in rows])
    st = np.column_stack([r[1] for r in rows])
    return s1, st


def _run_pawn_timeseries(problem, x, y2d, n_jobs=1, pawn_s=10, executor="thread"):
    ntime = y2d.shape[1]
    mode = _analysis_executor_mode(executor, "_run_pawn_timeseries")

    def _worker(i):
        out = pawn.analyze(problem, x, y2d[:, i], S=pawn_s, print_to_console=False)
        return np.asarray(out["median"], dtype=np.float64)

    rows = _parallel_map(_worker, range(ntime), n_jobs, executor=mode)
    return np.column_stack(rows)


def _run_pawn_aggregated(problem, x, y2d, metrics, n_jobs=1, pawn_s=10, executor="thread"):
    aggregated = _aggregate_outputs(y2d, metrics)
    mode = _analysis_executor_mode(executor, "_run_pawn_aggregated")

    def _worker(metric):
        out = pawn.analyze(problem, x, aggregated[metric][:, 0], S=pawn_s, print_to_console=False)
        return metric, np.asarray(out["median"], dtype=np.float64)

    rows = _parallel_map(_worker, metrics, n_jobs, executor=mode)
    return {metric: values for metric, values in rows}


def _run_sobol_aggregated(problem, y2d, metrics, n_jobs=1, executor="thread"):
    aggregated = _aggregate_outputs(y2d, metrics)
    mode = _analysis_executor_mode(executor, "_run_sobol_aggregated")

    def _worker(metric):
        si = sobol.analyze(problem, aggregated[metric][:, 0], print_to_console=False)
        s1 = np.asarray(si["S1"], dtype=np.float64)
        st = np.asarray(si["ST"], dtype=np.float64)
        return metric, s1, st

    rows = _parallel_map(_worker, metrics, n_jobs, executor=mode)
    s1 = {}
    st = {}
    for metric, s1_val, st_val in rows:
        s1[metric] = s1_val
        st[metric] = st_val
    return s1, st


def _run_sobol_from_metric_vectors(problem, metric_vectors, metrics, n_jobs=1, executor="thread"):
    mode = _analysis_executor_mode(executor, "_run_sobol_from_metric_vectors")

    def _worker(metric):
        si = sobol.analyze(problem, np.asarray(metric_vectors[metric], dtype=np.float64), print_to_console=False)
        return (
            metric,
            np.asarray(si["S1"], dtype=np.float64),
            np.asarray(si["ST"], dtype=np.float64),
        )

    rows = _parallel_map(_worker, metrics, n_jobs, executor=mode)
    s1 = {}
    st = {}
    for metric, s1_val, st_val in rows:
        s1[metric] = s1_val
        st[metric] = st_val
    return s1, st


def _forcing_eval_chunk(self, samples_chunk, myvars_list, forcing_fixed, n_param, metrics):
    chunk_payload = {v: {m: [] for m in metrics} for v in myvars_list}
    samples_arr = np.asarray(samples_chunk, dtype=np.float64)
    for row in samples_arr:
        parm_i = row[:n_param]
        spinup_i = row[n_param:]
        out_i = self.run_surrogate_forcing(
            parm_i,
            myvars_list,
            forcing_engineered=forcing_fixed,
            spinup=spinup_i,
        )
        for v in myvars_list:
            arr = np.asarray(out_i[v], dtype=np.float64).ravel()
            if "mean" in metrics:
                chunk_payload[v]["mean"].append(float(np.nanmean(arr)))
            if "accumulated" in metrics:
                chunk_payload[v]["accumulated"].append(float(np.nansum(arr)))
            if "std" in metrics:
                chunk_payload[v]["std"].append(float(np.nanstd(arr)))
    return chunk_payload


def _merge_metric_payload(global_payload, chunk_payload):
    for v in chunk_payload:
        for metric, values in chunk_payload[v].items():
            global_payload[v][metric].extend(values)


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


def _plot_metric_bars(values, row_labels, title, fname):
    arr = np.asarray(values, dtype=np.float64).ravel()
    fig_h = max(4.0, min(12.0, 0.35 * len(row_labels) + 2.0))
    fig, ax = plt.subplots(figsize=(10, fig_h))
    ypos = np.arange(len(row_labels))
    ax.barh(ypos, arr, color="tab:blue")
    ax.set_yticks(ypos)
    ax.set_yticklabels(row_labels)
    ax.set_xlabel("Sensitivity")
    ax.set_ylabel("Input")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight")
    plt.close(fig)


def GSA(self, myvars, n_saltelli=8192, n_jobs=1, output_dir=None, executor="thread"):
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
        self.sens_main[v], self.sens_tot[v] = _run_sobol_timeseries(
            problem, y2d, n_jobs=n_jobs, executor=executor
        )

    if output_dir is not None:
        plot_GSA(self, myvars_list, output_dir=output_dir)


def GSA_given_data_pawn(
    self,
    myvars,
    include_spinup=False,
    spinup_vars=None,
    metrics=None,
    n_jobs=1,
    pawn_s=10,
    executor="thread",
    var_executor=None,
    output_dir=None,
):
    t0 = time.perf_counter()
    myvars_list = _normalize_var_list(myvars)
    metric_list = _normalize_metric_list(metrics)
    x = np.asarray(self.samples, dtype=np.float64).transpose()
    names = _base_param_labels(self)
    if int(n_jobs) > 1:
        print(
            f"[GSA] PAWN parallelism note: {len(myvars_list)} vars x {len(metric_list)} metrics; "
            "speedup scales mainly when multiple vars are requested."
        )

    if include_spinup:
        spinup_names = list(DEFAULT_SPINUP_VARS if spinup_vars is None else spinup_vars)
        spinup = _collect_spinup_matrix(self, spinup_names)
        x = np.column_stack((x, spinup))
        names = names + [f"spinup_{v}" for v in spinup_names]

    bounds = np.column_stack((np.min(x, axis=0), np.max(x, axis=0)))
    problem = {"num_vars": int(x.shape[1]), "names": names, "bounds": bounds.tolist()}

    self.sens_pawn = {}
    self.sens_pawn_names = names
    self.sens_pawn_metrics = metric_list
    var_mode = _normalize_executor_mode("serial" if var_executor is None else var_executor)
    if var_mode == "process":
        print("[GSA] GSA_given_data_pawn var_executor=process not supported; using thread.")
        var_mode = "thread"
    analysis_mode = _analysis_executor_mode(executor, "GSA_given_data_pawn")

    def _var_worker(v):
        y2d = np.asarray(self.output[v], dtype=np.float64).transpose()
        if y2d.shape[0] != x.shape[0]:
            raise ValueError(
                f"Sample mismatch for {v}: X has {x.shape[0]} rows, output has {y2d.shape[0]} rows."
            )
        return v, _run_pawn_aggregated(
            problem,
            x,
            y2d,
            metric_list,
            n_jobs=n_jobs,
            pawn_s=int(pawn_s),
            executor=analysis_mode,
        )

    rows = _parallel_map(_var_worker, myvars_list, n_jobs=n_jobs, executor=var_mode)
    for v, payload in rows:
        self.sens_pawn[v] = payload
    _log_checkpoint("PAWN analysis complete", t0)

    plot_GSA_pawn(self, myvars_list, output_dir=output_dir)


def GSA_forcing_timeseries(
    self,
    myvars,
    n_saltelli=1024,
    spinup_vars=None,
    metrics=None,
    n_jobs=1,
    executor="thread",
    sobol_executor=None,
    chunk_size=None,
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
    metric_list = _normalize_metric_list(metrics)
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
    t0 = time.perf_counter()
    run_mode = _normalize_executor_mode(executor)
    sobol_mode = _normalize_executor_mode(run_mode if sobol_executor is None else sobol_executor)

    samples = saltelli.sample(problem, int(n_saltelli))
    n_param = int(self.nparms_ensemble)
    n_eval = samples.shape[0]
    worker_count = _resolve_worker_count(n_jobs, n_eval)
    eff_chunk = _resolve_chunk_size(chunk_size, n_eval, worker_count)
    _log_checkpoint("forcing setup complete", t0)

    aggregated_values = {v: {m: [] for m in metric_list} for v in myvars_list}
    if run_mode == "serial" or worker_count <= 1:
        for start in range(0, n_eval, eff_chunk):
            stop = min(start + eff_chunk, n_eval)
            chunk_payload = _forcing_eval_chunk(
                self,
                samples[start:stop, :],
                myvars_list,
                forcing_fixed,
                n_param,
                metric_list,
            )
            _merge_metric_payload(aggregated_values, chunk_payload)
    else:
        executor_cls = ProcessPoolExecutor if run_mode == "process" else ThreadPoolExecutor
        try:
            with executor_cls(max_workers=worker_count) as pool:
                futures = []
                for start in range(0, n_eval, eff_chunk):
                    stop = min(start + eff_chunk, n_eval)
                    futures.append(
                        pool.submit(
                            _forcing_eval_chunk,
                            self,
                            samples[start:stop, :],
                            myvars_list,
                            forcing_fixed,
                            n_param,
                            metric_list,
                        )
                    )
                for fut in futures:
                    _merge_metric_payload(aggregated_values, fut.result())
        except Exception:
            if run_mode != "process":
                raise
            print("[GSA] forcing process mode failed; retrying with thread executor.")
            with ThreadPoolExecutor(max_workers=worker_count) as pool:
                futures = []
                for start in range(0, n_eval, eff_chunk):
                    stop = min(start + eff_chunk, n_eval)
                    futures.append(
                        pool.submit(
                            _forcing_eval_chunk,
                            self,
                            samples[start:stop, :],
                            myvars_list,
                            forcing_fixed,
                            n_param,
                            metric_list,
                        )
                    )
                for fut in futures:
                    _merge_metric_payload(aggregated_values, fut.result())
    _log_checkpoint("forcing sample evaluation complete", t0)

    self.sens_forcing_main = {}
    self.sens_forcing_tot = {}
    self.sens_forcing_names = all_names
    self.sens_forcing_metrics = metric_list
    for v in myvars_list:
        metric_vectors = {
            metric: np.asarray(aggregated_values[v][metric], dtype=np.float64)
            for metric in metric_list
        }
        self.sens_forcing_main[v], self.sens_forcing_tot[v] = _run_sobol_from_metric_vectors(
            problem,
            metric_vectors,
            metric_list,
            n_jobs=n_jobs,
            executor=sobol_mode,
        )
    _log_checkpoint("forcing Sobol analysis complete", t0)

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
    metrics = _normalize_metric_list(getattr(self, "sens_pawn_metrics", None))
    for v in myvars_list:
        if v not in self.sens_pawn:
            continue
        metric_payload = {}
        metric_written = []
        for metric in metrics:
            if metric not in self.sens_pawn[v]:
                continue
            values = np.asarray(self.sens_pawn[v][metric], dtype=np.float64)
            metric_payload[f"median_{metric}"] = values
            metric_written.append(metric)
            _plot_metric_bars(
                values,
                names,
                f"PAWN median index ({metric}) - {v}",
                os.path.join(outdir, f"pawn_median_{v}_{metric}.png"),
            )
        np.savez(
            os.path.join(outdir, f"pawn_{v}.npz"),
            names=np.asarray(names, dtype=object),
            metrics=np.asarray(metric_written, dtype=object),
            **metric_payload,
        )


def plot_GSA_forcing(self, myvars, output_dir=None):
    outdir = _resolve_output_dir(self, output_dir)
    myvars_list = _normalize_var_list(myvars)
    names = list(getattr(self, "sens_forcing_names", _base_param_labels(self)))
    metrics = _normalize_metric_list(getattr(self, "sens_forcing_metrics", None))
    for v in myvars_list:
        if v not in self.sens_forcing_main:
            continue
        metric_payload = {}
        metric_written = []
        for metric in metrics:
            if metric not in self.sens_forcing_main[v] or metric not in self.sens_forcing_tot[v]:
                continue
            main = np.asarray(self.sens_forcing_main[v][metric], dtype=np.float64)
            tot = np.asarray(self.sens_forcing_tot[v][metric], dtype=np.float64)
            metric_payload[f"S1_{metric}"] = main
            metric_payload[f"ST_{metric}"] = tot
            metric_written.append(metric)
            _plot_metric_bars(
                main,
                names,
                f"Forcing surrogate Sobol S1 ({metric}) - {v}",
                os.path.join(outdir, f"forcing_sens_main_{v}_{metric}.png"),
            )
            _plot_metric_bars(
                tot,
                names,
                f"Forcing surrogate Sobol ST ({metric}) - {v}",
                os.path.join(outdir, f"forcing_sens_tot_{v}_{metric}.png"),
            )
        np.savez(
            os.path.join(outdir, f"forcing_sobol_{v}.npz"),
            names=np.asarray(names, dtype=object),
            metrics=np.asarray(metric_written, dtype=object),
            **metric_payload,
        )
