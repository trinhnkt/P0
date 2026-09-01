"""CL4KT-style KT: causal transformer (SimpleKT-compatible) + train-only InfoNCE.

Lee et al. 2022: contrastive views of sparse learning histories.
`forward(feats)` matches DKT/SimpleKT so `predict_sequential` stays valid.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class CL4KT(nn.Module):
    def __init__(
        self,
        n_kcs: int,
        hidden_size: int = 64,
        nhead: int = 4,
        nlayers: int = 2,
        dropout: float = 0.2,
        temp: float = 0.05,
        reg_cl: float = 0.1,
    ):
        super().__init__()
        self.n_kcs = n_kcs
        self.hidden_size = hidden_size
        self.temp = temp
        self.reg_cl = reg_cl
        self.embed = nn.Embedding(n_kcs * 2 + 1, hidden_size)
        layer = nn.TransformerEncoderLayer(
            d_model=hidden_size,
            nhead=nhead,
            dim_feedforward=4 * hidden_size,
            dropout=dropout,
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=nlayers)
        self.fc = nn.Linear(hidden_size, n_kcs)

    def _causal_encode(self, feats: torch.Tensor):
        # feats: [B, S] interaction ids (kc*2+correct); pad value 0 is a valid id,
        # so callers must not pad with 0. We use key padding via feats < 0 if present.
        x = self.embed(feats.clamp(min=0))
        seqlen = feats.size(1)
        attn = torch.triu(
            torch.ones(seqlen, seqlen, device=feats.device, dtype=torch.bool),
            diagonal=1,
        )
        pad = feats < 0
        if pad.any():
            x = x.masked_fill(pad.unsqueeze(-1), 0.0)
            h = self.encoder(x, mask=attn, src_key_padding_mask=pad)
        else:
            h = self.encoder(x, mask=attn)
        return h

    def forward(self, feats: torch.Tensor):
        h = self._causal_encode(feats)
        return torch.sigmoid(self.fc(h))

    def pooled(self, feats: torch.Tensor):
        h = self._causal_encode(feats)
        pad = feats < 0
        keep = (~pad).unsqueeze(-1).float()
        denom = keep.sum(dim=1).clamp(min=1.0)
        return (h * keep).sum(dim=1) / denom

    def infonce(self, z1, z2):
        z1 = F.normalize(z1, dim=-1)
        z2 = F.normalize(z2, dim=-1)
        logits = z1 @ z2.t() / self.temp
        labels = torch.arange(z1.size(0), device=z1.device)
        return F.cross_entropy(logits, labels)
