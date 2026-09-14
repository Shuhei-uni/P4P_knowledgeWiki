# P7-E4-ADAPT-G150 — conditional fourth adaptive screen at G=1.50

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | discovery adaptive short screen |
| Candidate/origin | E4-ADAPT conditional fourth branch; Phase Loop activation from CONTEXT.md on 2026-09-09 |
| Authority/gate | Human-approved bounded fourth rule recorded in CONTEXT.md; G1 recovery |
| Parent | Exact valid P7-E0-REF iteration-500 case/data checkpoint |
| Controlled delta | proven E3 bottom actuator with command=clamp(1.50 × 116.92 kg/s × e, 0, 146.15 kg/s) |
| Normalization | M*=149.424869 kg; DeltaMref=223.250694 kg from the E0 500--1000 history |
| Active horizon | 500 controller-active iterations; 50-iteration smoke; checkpoints active 50, 250, 500 |

## Selection rationale and limits

G=1.00 completed without saturation and ended with a positive inventory slope,
while its final command remained below the 146.15 kg/s cap. The context rule
therefore permits one higher-gain branch at G=1.50.

Record every 50-iteration inventory/error/command/readback update, phase split,
balance, residual, and artifact. High-gain cycling, saturation, numerical
failure, or vapor-dominated routing rejects the branch. No adaptive-control,
plant, or convergence claim is permitted.

