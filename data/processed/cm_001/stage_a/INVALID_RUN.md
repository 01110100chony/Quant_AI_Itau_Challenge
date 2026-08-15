# INVALID CM_001 Stage A run

This directory contains outputs from the first, invalid acquisition/parsing run.

Root cause: PowerShell `Export-Csv` serialized provider JSON numbers with locale decimal commas; the Python parser then created `NaN` values. Downstream empty-window and missing-component counts in this directory are invalid and must not be interpreted as market-data availability or scientific feasibility.

These files are preserved only for audit/debug provenance. The corrected artifacts are in `../stage_a_provider_audit_v2/` and the experiment reports. No file in this directory is canonical.
