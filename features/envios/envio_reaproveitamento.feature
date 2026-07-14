# language: pt

Funcionalidade: Reaproveitamento de contrato
  Como usuário da plataforma
  Quero reaproveitar um documento já enviado
  Para gerar um novo contrato sem repetir o upload

  @envio @ui @signature @regression
  Cenário: Reaproveitamento de documento enviado
    Dado que estou logado na plataforma D4Sign
    E que enviei um documento pela desk
    Quando reaproveito o documento para um cofre
    Então um novo documento deve ser criado aguardando signatários
