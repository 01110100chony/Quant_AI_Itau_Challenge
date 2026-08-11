# Dados

- `raw/`: snapshots recebidos da fonte, preservando timestamps e valores originais.
- `processed/`: transformações reproduzíveis geradas a partir de `raw/`.

Cada nova coleta deve registrar fonte, símbolos, período solicitado, data da coleta, timezone, campo de preço e política de ajustes. Não sobrescreva um snapshot raw sem preservar ou documentar a versão anterior.

