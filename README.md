# BairroAberto — The Sims 4 🏡

Projeto de mod de script **em desenvolvimento** para explorar um bairro
contínuo em The Sims 4: caminhar até as casas comuns dos vizinhos e visitá-las
sem telas de carregamento, como em The Sims 3.

**Ainda não é um mundo aberto funcional.** A versão experimental atual, 0.6.0,
pode registrar móveis durante uma visita e tentar montar **até 32 objetos**
do lote vizinho na zona ativa, de uma vez. Paredes, portas, moradores,
roteamento e visitas realmente sem loading ainda não foram implementados.
O jogo confirmou a criação e remoção de **um** objeto; a montagem de vários
objetos ainda precisa de teste in-game.

## Versões preservadas

O histórico do repositório contém commits sequenciais para:

| Versão | Conteúdo | Branch da versão |
| --- | --- | --- |
| 0.2.0 | Protótipo inicial recebido do usuário | [`versoes/v0.2.0`](../../tree/versoes/v0.2.0) |
| 0.3.0 | Identificação e inspeção de lotes vizinhos | [`versoes/v0.3.0`](../../tree/versoes/v0.3.0) |
| 0.4.0 | Inspeção segura de APIs de lote e zona | [`versoes/v0.4.0`](../../tree/versoes/v0.4.0) |
| 0.5.0 | Captura e preview experimental de um móvel | [`versoes/v0.5.0`](../../tree/versoes/v0.5.0) |
| 0.5.1 | Corrige a detecção de móveis no ObjectManager | [`versoes/v0.5.1`](../../tree/versoes/v0.5.1) |
| 0.5.2 | Preview deslocado para testar a renderização fora do lote | [`versoes/v0.5.2`](../../tree/versoes/v0.5.2) |
| 0.6.0 | Abertura experimental de um conjunto de móveis e limpeza conjunta | [`versoes/v0.6.0`](../../tree/versoes/v0.6.0) |

O código mais antigo disponível é a versão 0.2.0. Caminhos pessoais foram
anonimizados ao importar seu arquivo de instruções antigo. Arquivos de log
locais e saves **não** são publicados aqui.

## Compilar e testar

Consulte o [LEIAME.md](LEIAME.md) para as instruções completas em português.

No Windows, use o Python **3.7** dentro da pasta do projeto:

```cmd
py -3.7 build.py
```

Isso produz `dist/OpenNeighborhood.ts4script` e executa o verificador.
O nome interno `OpenNeighborhood` vem das primeiras versões do protótipo;
o nome público deste projeto é **BairroAberto**.

**Faça os testes apenas em uma cópia do save e não salve após executar**
`on.preview_one`, `on.preview_shift` ou `on.open_neighbor` — as cópias podem
persistir se o jogo travar ou forem gravadas antes da limpeza.

## Estado mais recente dos testes

Uma captura de tela da v0.5.0 mostrou que `on.capture_neighbor` descartou todos
os objetos; por isso `on.captured` e `on.preview_one` não encontraram o arquivo
de captura. A v0.5.1 ajusta as verificações e informa os motivos de descarte
em caso de nova falha. Em teste posterior, a v0.5.1 **capturou 132 objetos** e
registrou **uma criação e remoção bem-sucedidas** na simulação. Ainda falta
comprovar que a cópia aparece e pode ser usada fora do lote ativo. Consulte
[notas técnicas](docs/NOTAS_TECNICAS.md) para o histórico dos experimentos.

Na v0.5.2, `on.preview_shift 0 2 0` cria a cópia deslocada dois metros no
eixo X, permitindo diferenciá-la de um móvel que o jogo já esteja exibindo.
Remova-a com `on.preview_cleanup` e **não salve** depois do preview.

Na v0.6.0, `on.open_neighbor 8 0` tenta instanciar oito móveis da casa
vizinha nas posições originais, dentro da zona ativa. `on.close_neighbor`
destrói todas as cópias temporárias rastreadas. A quantidade pode ser ajustada
de 1 a 32; o segundo número é o índice inicial da captura. **Isso ainda não
importa paredes ou caminhos internos e não torna a casa visitável por si só.**

É necessário ter `OpenNeighborhood_capture.json` na pasta Mods. Se o arquivo
sumiu após a instalação de outra versão, o mod agora informa como refazer a
captura; atualizar o script não regenera sozinho os dados da casa vizinha.
