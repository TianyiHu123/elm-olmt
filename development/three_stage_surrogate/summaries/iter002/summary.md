# Iter002 Closeout Summary

- Iteration/work type: `iter002` / `implementation`
- Objective: implement and validate the pooled ABBY/JERC development-only spinup C/N baseline.
- Input snapshot: immutable `r0001`.
- Locked campaign-plan SHA-256:
  `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`.
- Result/decision: `pass` / `optimization_recommended`.
- Final interface: 25 fixed inputs; separate `(32,)` tanh/L-BFGS MLPs; standardized natural-log
  targets; exponentiated positive physical predictions; no site-identity input and no clipping.
- Split: smoke 80/20; operational 655/164 from the 819 development members; access to the 205
  fixed-test members remained false.
- Operational validation R2 (C/N): physical `0.6704/0.6696`; log `0.6880/0.6857`.
- Site log R2 (C/N): ABBY `0.8199/0.8157`; JERC `0.5914/0.5901`. Pooled physical bias
  (prediction minus ELM): `-23,778 gC/m2` and `-2,398 gN/m2`.
- Evidence: 24 train/validation metric rows, 12 validation-minus-training gap rows, four scatter
  plots, eight-repeat permutation importance, and flexible 1/7/20/164-member prediction all passed.
- Artifact: operational non-release SHA-256
  `4c42e818e124a2f72ed54635ae02979afeb7ec10518c15be187b8775e6947064`.
- Accounting: preflight `24450843`, corrected smoke `24450974`, operational `24451007`, validation
  `24453838`, and corrected-test preflight `24453852` completed `0:0`; initial smoke `24450877`
  failed the nonpositive-output gate and is preserved.
- Boundary: no fixed-test use, all-819 fit/prediction, release, GPP/SR work, tuning, or push.
- Output root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter002_abby_jerc_spinup_baseline`.
- Next direction: planning-only Iter003 bounded spinup-configuration experiment; fresh approval
  required.
