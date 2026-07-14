# language: pt

Funcionalidade: Envio via desk
  Como usuário da plataforma
  Quero enviar documento pela desk
  Para visualizar na viewblob

  @envio @ui @signature @critical
  Cenário: Envio de documento pela desk
    Dado que estou logado na plataforma D4Sign
    Quando envio um documento pela desk para assinatura
    Então o documento deve estar aguardando signatários
