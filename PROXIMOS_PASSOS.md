# Roteiro técnico: OpenNeighborhood

Objetivo final: sair do lote de casa, caminhar até casas comuns do mesmo
bairro e visitar seus interiores sem tela de carregamento, com experiência
parecida com The Sims 3.

## Estado atual: v0.5.2 (teste de renderização da cópia deslocada)

- Identificar zona atual, IDs dos lotes vizinhos e registros do ZoneManager.
- Mapear quais dados persistidos são acessíveis sem viajar.
- Inspecionar metadados (não chamar) de APIs nativas e classes de zona/lote.
- Capturar um subconjunto de móveis do lote vizinho quando ele estiver ativo.
- Tentar criar uma cópia de um móvel fora do lote atual e removê-la em seguida.
- Validar os comandos e o descarte dos previews num save descartável.

## Experimentos futuros, dependentes dos resultados

1. **Objetos e geometria:** validar o preview de **um móvel**, depois ampliar
   para conjuntos de móveis e geometria de paredes. Não é garantido que um
   objeto de outro lote seja renderizado ou interativo na zona atual.
2. **Portas e roteamento:** testar uma interação de visita e descobrir se o Sim
   consegue percorrer o trajeto até um interior simulado.
3. **Moradores:** testar surgimento, autonomia, permissões e retorno para casa.
4. **Persistência:** garantir que nenhum objeto duplicado ou visita altere o
   save indevidamente e que uma troca de lote limpe os objetos temporários.
5. **Compatibilidade:** testar em mundos diferentes e com atualizações do jogo.

Somente o começo experimental da etapa 1 foi implementado. O teste **ainda não
foi executado dentro do jogo** e deve falhar de modo explícito caso uma API
interna não aceite o objeto ou a posição. As etapas 2–5 seguem em aberto.
