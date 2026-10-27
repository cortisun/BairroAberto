# Open Neighborhood: diagnóstico v0.2.0

Não instale nada antes de o passo 2 dar **OK**.

## 1. Diagnosticar o pacote antigo (sem ativá-lo)

Qualquer Python 3.6+ serve para o verificador:

```
python verify_ts4script.py "C:\Users\SEU_USUARIO\OneDrive\Documentos\Electronic Arts\The Sims 4\Mods\OpenNeighborhood.ts4script.disabled" ^
  --compare "<algum mod que carrega bem>.ts4script" ^
  --resource-cfg "C:\Users\SEU_USUARIO\OneDrive\Documentos\Electronic Arts\The Sims 4\Mods\Resource.cfg"
```

Ele aponta: versão do bytecode, pasta-pai extra no ZIP, barras invertidas (`Compress-Archive`), compressão, ZIP64 e regras `.ts4script` no `Resource.cfg`.

## 2. Gerar o pacote corrigido (precisa do Python 3.7)

```
C:\Users\SEU_USUARIO\Documents\Codex\2026-10-20\ped\work\python37\runtime\python.exe build.py
```

O resultado fica em `dist\OpenNeighborhood.ts4script` e passa pelo verificador automaticamente. Ele recusa compilar fora do 3.7.

## 3. Instalar (só depois do OK)

1. Feche o jogo. Confirme que o jogo inicia com o protótipo desativado.
2. Copie o pacote para a pasta Mods, no máximo 1 subpasta de profundidade, ou use `build.py --install "<...>\Mods"`.
3. Mantenha o `.disabled` antigo fora da pasta Mods, ou apague-o.
4. A pasta Mods está no OneDrive: clique com o botão direito no arquivo e escolha **Sempre manter neste dispositivo**. Um arquivo só na nuvem, ou em sincronização, pode ser lido como corrompido.
5. Abra o jogo e vá em Opções > Outros > ative Mods de script. Depois, no console (Ctrl+Shift+C):
   - `open_neighborhood.status` (ou `on.status`)
   - `open_neighborhood.zones`
   - `open_neighborhood.native_api` ou `open_neighborhood.native_api zone`
6. Envie o arquivo `Mods\OpenNeighborhood_diag.txt`. Se ele existir mas os comandos não responderem, o import funcionou e o problema está no registro dos comandos. Se não existir, o módulo não foi importado.

## Segurança

Todos os comandos são de leitura: `dir()`/`type()` em módulos nativos que já estão em `sys.modules` (nada é importado nem chamado) e a leitura de `ZoneManager` e do protobuf do bairro. A DLL e os arquivos do jogo não são alterados.
