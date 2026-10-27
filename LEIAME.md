# OpenNeighborhood v0.4.0 — protótipo de investigação (não é mundo aberto ainda)

Este pacote evolui o diagnóstico v0.3.0. **Ainda não permite entrar na casa dos
vizinhos sem carregamento.** Ele identifica lotes vizinhos no save, mostra
quais IDs constam no ZoneManager e lê as assinaturas, descrições e membros
estáticos de classes relacionadas a lotes. Não executa as funções nativas
inspecionadas. O objetivo é preparar experimentos futuros com mais informação.

Não instale o ZIP de código-fonte em Mods. Ele **não** contém um `.ts4script`
compilado. O compilador precisa do Python 3.7 para produzir um `.ts4script`
compatível com o projeto original.

## 1. Preparar um teste com segurança

1. Faça backup do seu save do The Sims 4 e faça os testes numa **cópia** do save.
2. Deixe apenas um OpenNeighborhood ativo por vez. Tire a versão antiga da pasta
   Mods antes de instalar a nova.
3. Se o jogo já apresenta falhas sem este mod, resolva-as antes de começar.

## 2. Compilar no computador com Python 3.7

Extraia este ZIP numa pasta normal. Abra um terminal nessa pasta e execute com
o **Python 3.7**:

```cmd
py -3.7 build.py
```

O `build.py` verifica a versão, compila `src/open_neighborhood/*.py` e cria:

`dist/OpenNeighborhood.ts4script`

Depois executa `verify_ts4script.py`. Instale **somente se o verificador disser
OK**. O Python 3.12, 3.11 ou 3.8 não gera o bytecode necessário pelo compilador.

## 3. Instalar e registrar o bairro

1. Feche o The Sims 4. Copie somente `dist/OpenNeighborhood.ts4script` para
   `Documentos\Electronic Arts\The Sims 4\Mods` (ou uma subpasta diretamente
   dentro de Mods, nunca mais fundo).
2. Se a pasta estiver no OneDrive, mantenha o `.ts4script` disponível offline.
3. Ative os **Mods de script** nas opções do jogo e reinicie, se solicitado.
4. Entre num save de teste e abra o console com `Ctrl+Shift+C`.
5. Execute, nesta ordem:

```text
on.status
on.neighbors
on.native_info _buildbuy get_zones_cached_objects
on.native_info _buildbuy has_zone_cached_objects
on.class_api
```

Se quiser examinar um vizinho específico, execute `on.inspect <ID>` usando
um ID de `on.neighbors`. O comando não visita nem carrega esse lote.

6. Envie o arquivo `OpenNeighborhood_diag.txt`, criado na pasta `Mods`. Ele traz
   as observações necessárias para desenvolver o próximo experimento. Se o
   arquivo não aparecer, **não insista** com outros mods ativos; avise-nos.

## Comandos

| Comando | Efeito |
| --- | --- |
| `on.status` | Versão, Python, zona atual e local do log |
| `on.zones` | Diagnóstico de zonas da v0.2.0 |
| `on.neighbors` | Lista lotes e indica presença no ZoneManager; não prova carga do interior |
| `on.inspect <id>` | Mostra os campos do registro de uma zona escolhida |
| `on.native_api zone` | Procura nomes de APIs nativas, sem executá-las |
| `on.native_info <módulo> <função>` | Lê assinatura e documentação sem chamar a função |
| `on.class_api` | Inspeciona descritores das classes da zona e do lote ativos |

## 4. Testar o código fora do jogo (opcional)

Com um Python 3.7+ instalado, execute:

```text
python -m unittest discover -s tests -v
```

Os testes usam objetos simulados; passar neles **não** prova compatibilidade
com uma versão específica do The Sims 4.

## Segurança e limites

- Os comandos acrescentados nesta versão usam apenas APIs de observação e não
  criam casas, Sims, objetos ou zonas. Eles não modificam o save.
- O mod **não tem** função de viagem sem loading nesta versão.
- As APIs de cache ainda não foram chamadas: conhecemos apenas seus nomes e tipos.
- Metadados de lote não bastam para construir interiores completos; isso
  depende de APIs do jogo ainda não validadas.
- Teste somente numa cópia do save; patches do jogo podem quebrar mods.

Vídeo de referência: https://www.youtube.com/watch?v=iVXn-v1GGqU
