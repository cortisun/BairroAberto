# BairroAberto — The Sims 4 🏡

Projeto de mod de script **em desenvolvimento** para explorar um bairro
contínuo em The Sims 4: caminhar até as casas comuns dos vizinhos e visitá-las
sem telas de carregamento, como em The Sims 3.

**Ainda não é um mundo aberto funcional.** A versão experimental atual, 0.5.0,
pode registrar definições e posições de móveis enquanto o jogador visita um
lote e tentar recriar **um único objeto** fora do lote ativo depois. Paredes,
portas, moradores, roteamento e visitas realmente sem loading ainda não foram
implementados. A criação do objeto também aguarda validação no jogo.

## Versões preservadas

O histórico do repositório contém commits sequenciais para:

| Versão | Conteúdo | Branch da versão |
| --- | --- | --- |
| 0.2.0 | Protótipo inicial recebido do usuário | [`versoes/v0.2.0`](../../tree/versoes/v0.2.0) |
| 0.3.0 | Identificação e inspeção de lotes vizinhos | [`versoes/v0.3.0`](../../tree/versoes/v0.3.0) |
| 0.4.0 | Inspeção segura de APIs de lote e zona | [`versoes/v0.4.0`](../../tree/versoes/v0.4.0) |
| 0.5.0 | Captura e preview experimental de um móvel | [`versoes/v0.5.0`](../../tree/versoes/v0.5.0) |

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
`on.preview_one` — o objeto criado é experimental e pode persistir se houver
crash ou se o jogo for salvo antes da limpeza.

## Estado mais recente dos testes

O log recebido da v0.5.0 confirma carregamento com Python 3.7, mas ainda não
contém a execução dos comandos `on.capture_neighbor`, `on.captured`,
`on.preview_one` nem `on.preview_cleanup`. Consulte
[notas técnicas](docs/NOTAS_TECNICAS.md) para o histórico dos experimentos.
