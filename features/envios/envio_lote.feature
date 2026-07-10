# language: pt

Funcionalidade: Envio em lote
  Como usuário da plataforma
  Quero processar envios em lote via planilha
  Para automatizar múltiplos documentos

  @envio @ui @batch @regression
  Cenário: Envio em Lote
    Dado que estou logado na plataforma D4Sign
    Quando preparo e envio um lote com planilha Excel
    Então o lote deve ser processado com sucesso
