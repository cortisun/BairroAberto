# Notas dos testes (sem dados pessoais)

Estas anotações resumem o que foi observado nos logs enviados durante o
desenvolvimento. Os arquivos `OpenNeighborhood_diag*.txt` originais não entram
no GitHub, pois podem conter caminhos e informações de um computador pessoal.

## 0.2.0 → 0.3.0

- O `.ts4script` foi compilado com `py -3.7 build.py` no Windows e passou na
  verificação do ZIP: arquivos `.pyc` para Python 3.7, armazenados no pacote.
- O comando `on.neighbors` conseguiu ler registros de outros lotes presentes
  no bairro ativo, inclusive `zone_instance_id`, `lot_description_id` e
  `lot_template_id` quando disponíveis.
- O `ZoneManager` não mostrou interiores de vizinhos completamente ativos no
  primeiro teste. Após a troca de zona realizada pelo jogador, IDs anteriores
  podiam aparecer no gerenciador; **isso não prova interiores carregados**.

## 0.4.0

- O mod foi importado corretamente pelo jogo (Python 3.7.0).
- `_buildbuy.get_zones_cached_objects` descreve uma consulta a objetos em cache
  por tag, com estrutura `[zone_id, object_id, guid, name, description]`.
- `_buildbuy.has_zone_cached_objects` relata se há objetos de um tipo específico
  para uma zona. Sua presença não demonstra que o interior seja renderizável.
- A classe `zone.Zone` expõe operações de carregamento, inicialização,
  descarregamento e salvamento; são rotinas sensíveis e não foram chamadas.
- A classe `world.lot.Lot` expõe conversão de coordenadas entre lote e mundo.
  A relação entre transformações de lotes diferentes ainda deve ser validada.
- O jogador colocou móveis no lote da casa para permitir testes de objetos.

## 0.5.0

- O código agora tenta capturar definições e transformações de objetos na
  zona visitada. `on.preview_one` tenta duplicar **um objeto** na zona atual.
- Testes unitários locais foram executados, mas sem os módulos reais do jogo.
- Falta o primeiro log de execução in-game desta tentativa, especialmente
  para verificar `objects.system.create_object`, `routing.SurfaceIdentifier`,
  `sims4.math.Location` e a aceitação de posições fora do lote.
- Log recebido em 27/10/2026: o jogo confirmou `Open Neighborhood 0.5.0 loaded`
  e `python 3.7.0`. O arquivo continha chamadas antigas de `native_info` e
  `class_api`, mas nenhuma entrada `capture_neighbor`, `captured`,
  `preview_one` ou `preview_cleanup`. Portanto, ainda não há evidência
  suficiente para afirmar que o teste de criação de móveis funcionou.

## Questão central ainda em aberto

Não basta uma zona vizinha aparecer no save ou no `ZoneManager`. Para uma casa
realmente visitável, é necessário disponibilizar sua geometria (paredes,
andares e portas), móveis, roteamento, permissões e Sims na área simulada sem
transição de carregamento, e preservar o estado correto de cada lote no save.

Estas notas representam investigação e protótipos. Não constituem confirmação
de um mod completo de mundo aberto.
