"""Repository-scoped correction of emcee 3.1.6 DESnookerMove.get_proposal.

Adapted from emcee's MIT-licensed implementation, with the two corrections in
https://github.com/dfm/emcee/pull/531, merged as
946e6642fb68c70e64dc14c226c9fa0d4f0452b2.  The installed emcee package
remains unchanged for frozen Iter005 forensic replay.

The MIT License (MIT)
Copyright (c) 2010-2021 Daniel Foreman-Mackey & contributors.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import annotations

import emcee
import numpy as np


class DegenerateSnookerProposal(FloatingPointError):
    """The original selected points do not define a finite snooker proposal."""

    def __init__(self, message, *, details=None):
        super().__init__(message)
        self.details = {} if details is None else details


class CorrectedDESnookerMove(emcee.moves.DESnookerMove):
    """emcee's proposal with Euclidean unit direction and full Hastings power."""

    def get_proposal(self, s, c, random):
        ns = len(s)
        nc = list(map(len, c))
        ndim = s.shape[1]
        q = np.empty_like(s)
        metropolis = np.empty(ns, dtype=np.float64)
        if len(c) != 3 or any(count == 0 for count in nc):
            raise DegenerateSnookerProposal("snooker complement requires three nonempty groups",
                                            details={"partial_q": [], "failed_local_index": 0})
        for index in range(ns):
            w = np.array([c[j][random.randint(nc[j])] for j in range(3)])
            random.shuffle(w)
            z, z1, z2 = w
            delta = s[index] - z
            norm = np.linalg.norm(delta)
            if not np.isfinite(norm) or norm <= 0.0:
                raise DegenerateSnookerProposal(
                    "zero or nonfinite snooker reference distance",
                    details={"partial_q": q[:index].copy(), "failed_local_index": index,
                             "selected_reference": w.copy(), "sample": s[index].copy(),
                             "norm": norm},
                )
            direction = delta / norm
            q[index] = s[index] + direction * self.gammas * (
                np.dot(direction, z1) - np.dot(direction, z2)
            )
            new_norm = np.linalg.norm(q[index] - z)
            if not np.all(np.isfinite(q[index])) or not np.isfinite(new_norm) or new_norm <= 0.0:
                raise DegenerateSnookerProposal(
                    "zero or nonfinite snooker proposal distance",
                    details={"partial_q": q[:index].copy(), "failed_local_index": index,
                             "current_q": q[index].copy(), "selected_reference": w.copy(),
                             "sample": s[index].copy(), "norm": norm,
                             "new_norm": new_norm},
                )
            metropolis[index] = np.log(new_norm) - np.log(norm)
        factors = (ndim - 1.0) * metropolis
        if not np.all(np.isfinite(factors)):
            raise DegenerateSnookerProposal(
                "nonfinite snooker Hastings factor",
                details={"partial_q": q.copy(), "failed_local_index": ns,
                         "factors": factors.copy()},
            )
        return q, factors
