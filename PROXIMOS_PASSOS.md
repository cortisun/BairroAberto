# Roteiro técnico: OpenNeighborhood

Objetivo final: sair do lote de casa, caminhar até casas comuns do mesmo
bairro e visitar seus interiores sem tela de carregamento, com experiência
parecida com The Sims 3.

## Estado atual: v0.6.0 (montagem experimental de conjunto de móveis)

- Identificar zona atual, IDs dos lotes vizinhos e registros do ZoneManager.
- Mapear quais dados persistidos são acessíveis sem viajar.
- Inspecionar metadados (não chamar) de APIs nativas e classes de zona/lote.
- Capturar um subconjunto de móveis do lote vizinho quando ele estiver ativo.
- Tentar criar uma cópia de um móvel fora do lote atual e removê-la em seguida.
- Montar um grupo de até 32 móveis capturados na zona ativa, mantendo uma
  lista explícita de objetos temporários para limpeza coletiva.
- Validar os comandos e o descarte dos previews num save descartável.

## Experimentos futuros, dependentes dos resultados

1. **Objetos e geometria:** validar **visualmente** uma cópia e o grupo na
   v0.6.0; depois investigar geometria de pisos, paredes e portas. Não é
   garantido que um objeto de outro lote seja renderizado ou interativo.
2. **Portas e roteamento:** testar uma interação de visita e descobrir se o Sim
   consegue percorrer o trajeto até um interior simulado.
3. **Moradores:** testar surgimento, autonomia, permissões e retorno para casa.
4. **Persistência:** garantir que nenhum objeto duplicado ou visita altere o
   save indevidamente e que uma troca de lote limpe os objetos temporários.
5. **Compatibilidade:** testar em mundos diferentes e com atualizações do jogo.

A captura e a criação/remoção de **um** objeto foram confirmadas dentro do jogo.
A montagem de grupos da v0.6.0 passou em testes Python simulados, mas ainda
aguarda validação no jogo. As etapas 2–5 seguem em aberto.
