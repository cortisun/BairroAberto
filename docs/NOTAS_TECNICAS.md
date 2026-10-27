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
- Em uma captura de tela posterior, o comando `on.capture_neighbor` falhou
  informando que nenhum objeto era elegível. Como a captura não gerou arquivo,
  `on.captured` e `on.preview_one` acusaram arquivo ausente. O comando de
  limpeza informou zero objetos, como esperado após nenhum preview criado.

## 0.5.1

- Corrige a avaliação de flags (`is_sim` e `is_in_inventory`) quando fornecidas
  como métodos. Na versão anterior, métodos vinculados podiam ser tratados
  incorretamente como `True`, descartando todos os objetos.
- Prioriza `ObjectManager.get_all()` e usa `values()` como alternativa.
- Se a captura ainda retornar zero móveis, apresenta número de objetos
  examinados e categorias de rejeição para permitir uma correção específica.
- Teste dentro do The Sims 4 confirmado em 27/10/2026: foram examinados **280**
  objetos e **132** foram capturados. Os **148** restantes eram Sims ou objetos
  anexados, conforme o filtro atual.
- A primeira execução de `on.preview_one 0` foi bloqueada porque o ID da zona
  ativa ainda coincidia com o ID capturado. `on.preview_cleanup` informou
  `removed=0`, comportamento esperado nesse caso.
- Em uma segunda tentativa, `on.preview_one 0` confirmou a criação de um novo
  objeto com ID de instância. Depois `on.preview_cleanup` confirmou
  `removed=1, remaining=0`. Portanto, criação e remoção foram exercitadas
  pelo motor do jogo, mas **a renderização visual e a possibilidade de
  interação fora do lote ativo ainda não foram confirmadas**.
- A conclusão acima usa apenas um resumo do log; o log original e os IDs do
  save não foram incluídos no repositório público.

## Questão central ainda em aberto

Não basta uma zona vizinha aparecer no save ou no `ZoneManager`. Para uma casa
realmente visitável, é necessário disponibilizar sua geometria (paredes,
andares e portas), móveis, roteamento, permissões e Sims na área simulada sem
transição de carregamento, e preservar o estado correto de cada lote no save.

Estas notas representam investigação e protótipos. Não constituem confirmação
de um mod completo de mundo aberto.
