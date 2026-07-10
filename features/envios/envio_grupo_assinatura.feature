# language: pt

Funcionalidade: Envio para grupo de assinatura
  Como usuário da plataforma
  Quero enviar documento para um grupo de assinatura
  Para agilizar coleta de assinaturas

  @envio @ui @signature @regression
  Cenário: Upload de Documento
    Dado que estou logado na plataforma D4Sign
    Quando envio um documento pela desk para assinatura
    Então o documento deve estar aguardando signatários

  @envio @ui @signature @regression
  Cenário: Envio para Grupo de Assinatura
    Dado que estou logado na plataforma D4Sign
    E que enviei um documento pela desk
    Quando envio o documento para grupo de assinatura
    Então o documento deve estar na fase enviado
