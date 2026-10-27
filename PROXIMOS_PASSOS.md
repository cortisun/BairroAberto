# Roteiro técnico: OpenNeighborhood

Objetivo final: sair do lote de casa, caminhar até casas comuns do mesmo
bairro e visitar seus interiores sem tela de carregamento, com experiência
parecida com The Sims 3.

## Estado atual: v0.3.0 (investigação)

- Identificar zona atual, IDs dos lotes vizinhos e quais instâncias existem.
- Mapear quais dados persistidos são acessíveis sem viajar.
- Testar os comandos em um save descartável; receber log do usuário.

## Experimentos futuros, dependentes dos resultados

1. **Objetos e geometria:** testar, em isolamento, se móveis e paredes da casa
   vizinha podem ser representados na área carregada, sem viajar. Não é
   garantido que uma casa vista de fora tenha todos os dados carregados.
2. **Portas e roteamento:** testar uma interação de visita e descobrir se o Sim
   consegue percorrer o trajeto até um interior simulado.
3. **Moradores:** testar surgimento, autonomia, permissões e retorno para casa.
4. **Persistência:** garantir que nenhum objeto duplicado ou visita altere o
   save indevidamente e que uma troca de lote limpe os objetos temporários.
5. **Compatibilidade:** testar em mundos diferentes e com atualizações do jogo.

Nenhuma das etapas 1–5 foi implementada nesta versão. A demonstração de outro
criador mostra uma direção promissora, mas não disponibiliza aqui suas APIs
ou código-fonte. Nunca devemos anunciar 'mundo aberto pronto' sem teste real.
