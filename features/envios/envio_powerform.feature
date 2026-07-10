# language: pt

Funcionalidade: PowerForm
  Como usuário da plataforma
  Quero criar e enviar um PowerForm
  Para documentos a preencher

  @envio @ui @regression
  Cenário: Preparação do PowerForm
    Dado que estou logado na plataforma D4Sign
    Quando preparo e envio um PowerForm
    Então o PowerForm deve ser enviado com sucesso
