# language: pt

Funcionalidade: Visualização do embed de assinatura
  Como signatário
  Quero abrir o documento D4Sign via embed no editor Tryit
  Para visualizar a viewblob e conferir os anexos sem assinar

  @embed @ui @critical @embed
  Cenário: Visualizar viewblob via embed e contar anexos
    Dado que abro o editor Tryit do W3Schools
    Quando monto o embed do documento D4Sign para visualização
    Então a viewblob deve ser exibida no iframe do embed
    E o documento deve ter 3 anexos visíveis pelos canvas
