# language: pt

Funcionalidade: Envio pelo cofre
  Como usuário da plataforma
  Quero enviar documento dentro de um cofre
  Para visualizar na viewblob

  @envio @ui @signature @critical
  Cenário: Envio
    Dado que estou logado na plataforma D4Sign
    Quando envio um documento pelo cofre
    Então o documento deve estar aguardando signatários
