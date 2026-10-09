# language: pt

Funcionalidade: Consulta de documentos no cofre compartilhado
  Como usuário da plataforma
  Quero pesquisar o cofre compartilhado, a pasta compartilhada e a subpasta compartilhada e abri-los
  Para conferir a quantidade de documentos em cada um

  @cofre @cofre-compartilhado @pasta @subpasta @ui @smoke
  Cenário: Pesquisar e abrir cofre compartilhado, pasta compartilhada e subpasta compartilhada
    Dado que estou logado na plataforma D4Sign
    Quando pesquiso o cofre "Automação compartilhado - conta de automação"
    E abro o cofre "Automação compartilhado - conta de automação"
    Então a quantidade de documentos deve ser apresentada por nome
    Quando pesquiso a pasta "Pasta de Automação"
    E abro a pasta "Pasta de Automação"
    Então a quantidade de documentos deve ser apresentada por nome
    Quando pesquiso a pasta "Subpasta - Compartilhada"
    E abro a pasta "Subpasta - Compartilhada"
    Então a quantidade de documentos deve ser apresentada por nome
