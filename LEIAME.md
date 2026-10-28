# BairroAberto v0.6.0 — montagem experimental do interior vizinho

Projeto original para tentar transformar bairros de **The Sims 4** em espaços
contínuos como em The Sims 3: visitar casas comuns de vizinhos, sem tela de
carregamento. O alvo final continua sendo uma casa completa (móveis, paredes,
portas, Sims e caminhos jogáveis), não apenas a vizinhança decorativa.

**Estado atual: protótipo experimental, NÃO é um bairro aberto completo.**

A v0.5.0 acrescentou o primeiro teste de criação real de objeto: visita-se uma
casa vizinha normalmente uma vez, salva-se uma lista limitada de seus objetos,
volta-se ao lote de origem e pede-se que o mod tente recriar **um objeto** na
posição original que ele ocupava no mundo. O resultado pode não aparecer ou
ser rejeitado pelo motor do jogo. Nenhuma casa inteira é importada.

## Histórico do projeto

- `v0.2.0`: código-fonte inicial recuperado do ZIP disponibilizado pelo usuário.
- `v0.3.0`: identifica registros de lotes vizinhos sem forçar a carga deles.
- `v0.4.0`: investiga APIs nativas e classes de lote/zona com inspeção estática.
- `v0.5.0`: captura objetos do lote visitado e oferece pré-visualização manual
  de **um** objeto na zona ativa, com comando de limpeza.
- `v0.5.1`: corrige flags expostas pelo jogo como funções e prioriza
  `ObjectManager.get_all()` na captura; descreve motivos de descarte.
- `v0.5.2`: permite deslocar uma cópia de móvel em até 3 metros para distinguir
  visualmente o objeto do mod de uma representação já mostrada pelo jogo.
- `v0.6.0`: tenta reconstruir grupos de até 32 móveis, com fechamento e
  remoção de todas as cópias temporárias.

As branches `versoes/v...` preservam cada uma dessas versões no GitHub.
Não temos um arquivo v0.1.0,
por isso a linha do tempo começa na v0.2.0.

## Compilar no Windows

1. Tenha o **Python 3.7** instalado. Feche The Sims 4.
2. Abra um CMD dentro da pasta extraída do projeto.
3. Execute `py -3.7 build.py`.
4. Confirme que a verificação termina com `result: OK`.
5. Copie `dist\OpenNeighborhood.ts4script` para
   `Documentos\Electronic Arts\The Sims 4\Mods`.
6. Deixe só uma versão de OpenNeighborhood nessa pasta (no máximo uma subpasta
   abaixo de Mods), habilite mods de script e reinicie o jogo.

O ZIP de **código-fonte não vai diretamente em Mods**. Ele serve para gerar
`.ts4script` compatível com Python 3.7. O script não depende da Community Library.

## Teste da v0.6.0 (somente numa CÓPIA do save)

**Risco experimental:** duplicatas podem permanecer gravadas se você salvar
durante o teste ou se o jogo encerrar antes da limpeza. Faça backup de `saves`,
use uma cópia do save e **não salve o jogo depois de executar open_neighbor**.
Evite interagir com cópias temporárias durante a investigação.

1. Entre normalmente na casa do vizinho que quer abrir. O deslocamento
   inicial ainda tem tela de carregamento.
2. Abra o console (`Ctrl + Shift + C`) e digite `on.status` para confirmar a
   versão `0.6.0`.
3. Ainda dentro da casa vizinha, execute `on.capture_neighbor`, se o arquivo
   `OpenNeighborhood_capture.json` não existir ou estiver desatualizado.
4. Volte para sua casa normalmente e execute `on.captured`. A lista completa,
   com índices dos móveis, ficará em `Mods\OpenNeighborhood_diag.txt`.
5. Execute `on.open_neighbor 8 0`: o mod tentará criar os oito primeiros
   móveis registrados na zona ativa, nas posições da casa vizinha. Veja no
   console quantos objetos foram realmente criados.
6. Observe se os objetos estão visíveis atrás das janelas e se o Sim consegue
   chegar até perto da casa. **Não salve**. Execute `on.close_neighbor` e
   confira que os objetos pendentes chegaram a zero.
7. Se o primeiro grupo funcionar, em uma nova sessão descartável teste
   `on.open_neighbor 16 0` ou outro intervalo de até 32 objetos.
8. Envie o `OpenNeighborhood_diag.txt` e diga se houve móveis visíveis,
   invisíveis ou erros. As paredes/portas ainda não são importadas.

`on.capture_neighbor` cria `Mods\OpenNeighborhood_capture.json`, que guarda
somente IDs, posições e rotações dos objetos; não muda os móveis reais.
`on.captured` consulta essa lista. O preview não move nem apaga objetos do
vizinho: só tenta criar um novo objeto na zona atual.

## Comandos disponíveis

| Comando | Função |
| --- | --- |
| `on.status` | Verificar versão e zona atual |
| `on.neighbors` | Listar registros dos lotes próximos |
| `on.inspect <zona>` | Examinar registro de um lote |
| `on.zones` | Ver ZoneManager |
| `on.native_api`, `on.native_info`, `on.class_api` | Inspecionar APIs |
| `on.capture_neighbor` | Guardar mobília do lote visitado |
| `on.captured` | Listar objetos capturados e seus índices |
| `on.preview_one <indice>` | Tentar instanciar UM objeto no espaço original |
| `on.preview_shift <indice> <dx> <dz>` | Instanciar UM objeto deslocado (dx/dz de -3 a 3) |
| `on.preview_cleanup` | Destruir apenas objetos experimentais criados pelo mod |
| `on.open_neighbor <quantidade> <indice_inicial>` | Montar de 1 a 32 móveis temporários do vizinho |
| `on.close_neighbor` | Remover todas as cópias do interior experimental |

## Limites conhecidos

- Não há importação de arquitetura, paredes, portas, cobertura ou terrenos.
- Um conjunto de móveis **não** é uma casa visitável e pode não ter caminho
  de interação fora do lote ativo.
- Ainda não há chegada sem loading ao interior real: a visita inicial serve
  apenas para capturar o estado da casa. É uma etapa de investigação jogável.
- Nem todos os objetos podem ser recriados; APIs internas mudam entre patches.
- A limpeza só acompanha objetos criados nesta sessão. Um travamento do jogo
  impede a limpeza, por isso a regra de **não salvar** é importante.
- O teste de deslocamento pode colocar um móvel temporário sobre outra coisa,
  atrás de uma parede ou fora da câmera. Isso não confirma por si só que a
  renderização off-lot funcione ou falhe.
- Passar nos testes locais prova apenas a lógica Python simulada; não confirma
  que o jogo aceitará criar objetos na zona ativa fora do lote.

## Testes locais

```text
python -m unittest discover -s tests -v
```

## Referência visual da ideia

Vídeo mostrado pelo usuário: https://www.youtube.com/watch?v=iVXn-v1GGqU

O projeto aqui é próprio; nenhum código do vídeo foi incorporado.
