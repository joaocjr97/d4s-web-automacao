# language: pt

Funcionalidade: Consulta de documentos no cofre
  Como usuário da plataforma
  Quero pesquisar o cofre, a pasta e a subpasta e abri-los
  Para conferir a quantidade de documentos em cada um

  @cofre @cofre-normal @pasta @subpasta @ui @smoke
  Cenário: Pesquisar e abrir cofre, pasta e subpasta
    Dado que estou logado na plataforma D4Sign
    Quando pesquiso o cofre "12"
    E abro o cofre "12"
    Então a quantidade de documentos deve ser apresentada por nome
    Quando pesquiso a pasta "pasta"
    E abro a pasta "pasta"
    Então a quantidade de documentos deve ser apresentada por nome
    Quando pesquiso a pasta "subpasta"
    E abro a pasta "subpasta"
    Então a quantidade de documentos deve ser apresentada por nome
